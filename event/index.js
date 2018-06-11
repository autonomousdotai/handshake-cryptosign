const cron = require('node-cron');

const configs = require('./configs');
const constants = require('./constants');
const axios = require('axios');
const moment = require('moment');
// models
const models = require('./models');

// daos
const txDAO = require('./daos/tx');
const eventDAO = require('./daos/event');
const oddsDAO = require('./daos/odds');
const matchDAO = require('./daos/match');
const outcomeDAO = require('./daos/outcome');

const resource = require('./libs/resource')
const predictionContract = require('./libs/smartcontract');

// Add the web3 node module
const Web3 = require('web3');

// mark as running
let isRunning = false;
let isRunningOdds = false;
let isRunningCreateMarket = false;

const network_id = configs.network_id;

var BettingHandshake = getCompilied('PredictionHandshake');

var web3 = new Web3(new Web3.providers.HttpProvider(configs.network[network_id].blockchainNetwork));
var contractBettingAddress = configs.network[network_id].bettingHandshakeAddress;
var contractBettingHandshake = new web3.eth.Contract(BettingHandshake.abi, contractBettingAddress);

const allEvents = [
    '__createMarket',
	'__init',
	'__uninit',
	'__shake',
	'__collect',
	'__refund',
	'__report',
];

function getCompilied(contractName) {
	return require('./contracts/' + contractName + '.json');
}

function parseOffchain(offchain) {
    let values = offchain.replace(/\u0000/g, '').split("_")
    console.log(values)
    if (values.length >= 2) {
        return [values[0].trim(), values[1].trim()];
    } else {
        return null;
    }
}

function callEvent(eventName, eventObj) {
    console.log(eventName + " hid = " + eventObj.returnValues.hid);
    console.log(eventName + " offchain = " + eventObj.returnValues.offchain);
    const hid = eventObj.returnValues.hid;
    const offchain = eventObj.returnValues.offchain;
    if (hid == undefined || offchain == undefined) {
        console.log("missing parameters");
        return;
    }
    let offchainStr = Web3.utils.toAscii(offchain);
    let offchains = parseOffchain(offchainStr);
    console.log("offchains", offchains);
    if (offchains !== null) {
        let offchainType = offchains[0];
        if (offchainType == constants.CRYPTOSIGN_OFFCHAIN_PREFIX) {
            const offchainId = offchains[1];
            const events = {};
            const body = {};
            events['hid'] = hid;
            events['offchain'] = offchainId;
            events['eventName'] = eventName;
            events['contract'] = BettingHandshake.contractName;
            body['events'] = events;
            axios.post(configs.restApiEndpoint + '/event', body)
            .then(function (response) {
                console.log('hook success');
            })
            .catch(function (error) {
                console.log('hook failed');
            });
        }
    }
}

async function processEventObj(contractAddress, eventName, eventObj) {
    let tx = await models.sequelize.transaction();
    try {
        await eventDAO.create(tx, contractAddress, eventName, JSON.stringify(eventObj), eventObj.blockNumber, eventObj.logIndex);
        console.log("eventName = " + eventName);
        switch (contractAddress) {
            case contractBettingAddress: {
                switch (eventName) {
                    case '__createMarket':
                    case '__init':
                    case '__shake':
                    case '__uninit':
                    case '__report':
                    case '__collect':
                    case '__refund': {
                        callEvent(eventName, eventObj);
                    }
                        break;
                }
            }
                break;
        }
        tx.commit();
    } catch (err) {
        console.log('processEventObj', err);
        tx.rollback();
    }
}

function asyncGetPastEvents(contract, contractAddress, eventName, fromBlock) {
    return new Promise(function (resolve, reject) {
        contract.getPastEvents(eventName, {
            filter: {_from: contractAddress},
            fromBlock: fromBlock,
            toBlock: 'latest'

        }, function (error, events) {
            console.log(eventName + " getPastEvents OK")
            resolve(events);
            // if (error != null) {
            //     reject(error);
            // } else {
            //     resolve(events);
            // }
        });
    })
}

function submitInitTransactions(dataInit, total, success) {
    return new Promise(function (resolve, reject) {
        const tnx_tasks = [];
        dataInit.forEach((item, index) => {
            tnx_tasks.push(new Promise((resolve, reject) => {
                predictionContract
                .submitInitTransaction(index, item.hid, item.side, item.payout, item.offchain, item.value)
                .then(resultInit => {
                    console.log('Bot bet success', resultInit);
                    success += 1;
                    resolve();
                })
                .catch(e => {
                    console.error('bet error: ', e);
                    resolve();
                })
            }));
        });
        Promise.all(tnx_tasks)
        .then(result => {
            return resolve(`${success}/${total}`);
        })
        .catch(reject);
    });
};

async function asyncScanEventLog(contract, contractAddress, eventName) {
    let lastEventLog = await eventDAO.getLastLogByName(contractAddress, eventName);
    var fromBlock = 0;
    if (lastEventLog != null) {
        fromBlock = lastEventLog.block + 1;
    }
    console.log(eventName + " fromBlock = " + fromBlock);
    let events = await asyncGetPastEvents(contract, contractAddress, eventName, fromBlock);
    if (events !== undefined) {
        for (var i = 0; i < events.length; i++) {
            const eventObj = events[i];
            console.log(eventObj);
            let checkEventLog = await eventDAO.getByBlock(contractAddress, eventObj.blockNumber, eventObj.logIndex);
            if (checkEventLog == null) {
                await processEventObj(contractAddress, eventName, eventObj);
            }
        }
    }
}

function asyncScanOddsNull() {
    return new Promise(async (resolve, reject) => {
        const supports = await oddsDAO.getSupportOddsNull();
        const againsts = await oddsDAO.getAgainstOddsNull();

        let dataInit = [];
        const tasks = [];

        const submitInit = (arr, side) => {
            arr.forEach(item => {
                tasks.push(new Promise(async (_resolve, _reject) => {
                    const match = await matchDAO.getMatchById(item.match_id);
                    const amount = '0.1';
                    resource
                        .submitInit(item, match.toJSON(), configs.network[network_id].ownerAddress, side, network_id, amount)
                        .then(response => {
                            if (response.status == 1 && response.status_code == 200 && response.data.length != 0) {
                                dataInit.push({
                                    hid: item.hid,
                                    payout: web3.utils.toWei(response.data[0].odds + ""),
                                    value: web3.utils.toWei(amount),
                                    offchain: response.data[0].offchain,
                                    side: side
                                });
                            }
                            _resolve(null)
                        })
                        .catch((e) => {
                            console.log('Bot bet error', item, e);
                            _resolve(null);
                        }); 
                }))   
            });
        };

        if (againsts) {
            submitInit(againsts, 2);
        }
        if (supports) {
            submitInit(supports, 1);
        }

        if (tasks.length > 0) {
            Promise
                .all(tasks)
                .then(() => {
                    if (dataInit.length === 0) {
                        return resolve(0);
                    }
                    let success = 0;
                    submitInitTransactions(dataInit, tasks.length, success).then(resolve).catch(reject);
                })
                .catch(reject);
        } else {
            resolve(0);
        }
    });
}

function asyncScanOutcomeNull() {
    return new Promise(async(resolve, reject) => {
        const outcomes = await outcomeDAO.getOutcomesNullHID();
        if (outcomes.length > 0) {
            tasks = []
            outcomes.forEach((outcome, index) => {
                const task = new Promise(async(resolve, reject) => {
                    const match = await matchDAO.getMatchById(outcome.match_id);
                    const fee = match.market_fee;
                    const closingTime = match.date - Math.floor(+moment.utc()/1000);
                    const reportTime = closingTime + (4 * 60 * 60);
                    const dispute = reportTime + (4 * 60 * 60);
                    const offchain = `createMarket_${outcome.id}`;
                    const source = match.source;

                    predictionContract
                        .createMarketTransaction(index, fee, source, closingTime, reportTime, dispute, offchain)
                        .then((receipt) => {
                            console.log(`Create outcome ${outcome.id} success, Receipt: ${receipt}`);
                            resolve(hash);
                        })
                        .catch((e) => {
                            console.log(`Create outcome ${outcome.id} fail: ${e.message}`);
                            resolve(null);
                        });
                });
                tasks.add(task);
            });
            Promise.all(tasks).then((results) => {
                let success = 0;
                (results || []).forEach((hash) => {
                    if (hash) {
                        success += 1
                    }
                });
                resolve(success);
            })
        } else {
            resolve(0)
        }
    });
}

function runBettingCron() {
	cron.schedule('*/40 * * * * *', async function() {
		console.log('running a task every 40s at ' + new Date());
		try {
			if (isRunning === false) {
				isRunning = true;
				if (contractBettingHandshake && contractBettingHandshake != '') {
					for (var i = 0; i < allEvents.length; i++) {
						var eventName = allEvents[i];
						await asyncScanEventLog(contractBettingHandshake, contractBettingAddress, eventName);
					}
				}

				isRunning = false;
			}
			
		} catch (e) {
			isRunning = false;
			console.log('cron error');
			console.error(e);
		}
	});
}

function runOddsCron() {
    // cron.schedule('* 1 * * * *', async function() {
    cron.schedule('*/1 * * * *', async function() {
        console.log(configs);
		console.log('odds cron running a task every 1m at ' + new Date());
		try {
			if (isRunningOdds === false) {
                isRunningOdds = true;
                
                asyncScanOddsNull()
                    .then(result => {
                        console.log('EXIT ODDS: ', result);
                        isRunningOdds = false;
                    }).catch(e => {
                        console.log('EXIT ODDS: ', e);
                        isRunningOdds = false;
                    });

			} else {
                console.log('CRON JOB IS RUNNING!');
            }
			
		} catch (e) {
			isRunningOdds = false;
			console.log('cron odds error');
			console.error(e);
		}
	});
}

function runCreateMarketCron() {
    cron.schedule('*/1 * * * *', async function() {
        console.log(configs);
		console.log('create market cron running a task every 2m at ' + new Date());
		try {
			if (isRunningCreateMarket === false) {
                isRunningCreateMarket = true;
                
                asyncScanOutcomeNull().then(result => {
                    console.log('EXIT CREATE MARKET: ', result);
                    isRunningCreateMarket = false;
                });

			} else {
                console.log('CRON JOB CREATE MARKET IS RUNNING!');
            }
			
		} catch (e) {
			isRunningCreateMarket = false;
			console.log('cron create marjet error');
			console.error(e);
		}
	});
}

runBettingCron();
// runOddsCron();
runCreateMarketCron();