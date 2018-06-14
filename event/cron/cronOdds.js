const cron = require('node-cron');
const configs = require('../configs');

// daos
const matchDAO = require('../daos/match');
const handshakeDAO = require('../daos/handshake');
const settingDAO = require('../daos/setting');

const resource = require('../libs/utils')
const predictionContract = require('../libs/smartcontract');

const web3 = require('../configs/web3').getWeb3();

const ownerAddress = configs.network[configs.network_id].ownerAddress;
const oddsDefaultValue = configs.network[configs.network_id].oddsValue;

// mark as running
let isRunningOdds = false;

function submitInitTransactions(dataInit, total, success) {
    return new Promise( async (resolve, reject) => {
        try {
            const setting = await settingDAO.getByName('MarketCronJob');
            if (!setting) {
                console.log('MarketCronJob is null. Exit!');
                return;
            }
            if(!setting.status) {
                console.log('Exit MarketCronJob with status: ' + setting.status);
                return;
            }
            console.log('Begin run MarketCronJob!');

            const nonce = await resource.getNonceFromAPI(ownerAddress, dataInit.length);
            const tnx_tasks = [];
            dataInit.forEach((item, index) => {
                tnx_tasks.push(new Promise((resolve, reject) => {
                    predictionContract
                    .submitInitTransaction(nonce + index, item.hid, item.side, item.odds, item.offchain, item.value)
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
        } catch (e) {
            console.error('submit InitTransactions err: ', e);
            reject(e);
        }
    });
};

function asyncScanOddsNull() {
    return new Promise(async (resolve, reject) => {
        try {
            const supportsNull = await handshakeDAO.getSupportOddsNull();
            const againstsNull = await handshakeDAO.getAgainstOddsNull();
            const allNull = await handshakeDAO.getOddsNull();

            let dataInit = [];
            const tasks = [];

            const submitInit = (arr, side) => {
                arr.forEach(item => {
                    if (item ) {
                        tasks.push(new Promise(async (_resolve, _reject) => {
                            const match = await matchDAO.getMatchById(item.outcome.match_id);
                            const amount = oddsDefaultValue + '';
                            resource
                            .submitInit(item.outcome, match.toJSON(), configs.network[configs.network_id].ownerAddress, side, configs.network_id, amount, item.odds)
                            .then(response => {
                                if (response.status == 1 && response.data.length != 0) {
                                    dataInit.push({
                                        hid: item.outcome.hid,
                                        odds: parseInt(response.data[0].odds  * 100),
                                        value: web3.utils.toWei(amount),
                                        offchain: response.data[0].offchain,
                                        side: side
                                    });
                                } else {
                                    console.error(response);
                                    console.log(item);
                                }
                                _resolve(null)
                            })
                            .catch((e) => {
                                console.log('Bot bet error', item, e);
                                _resolve(null);
                            }); 
                        }));
                    }
                });
            };

            if (supportsNull) {
                const supArr = await resource.gennerateOddsArr(supportsNull, true);
                // console.log('SUPP');
                // console.log(supArr);
                submitInit(supArr, 1);
            }
            if (againstsNull) {
                const agaArr = await resource.gennerateOddsArr(againstsNull, false);
                // console.log('AGAINST');
                // console.log(agaArr);
                submitInit(agaArr, 2);
            }
            if (allNull) {
                const sups = [];
                const agas = [];
                (allNull || []).forEach(outcome => {
                    sups.push({
                        odds: resource.randomOdds(1),
                        outcome: outcome,
                        isSup: true
                    });
                    agas.push({
                        odds: resource.randomOdds(2),
                        outcome: outcome,
                        isSup: false
                    });
                });
                // console.log('============');
                // console.log(sups);
                // console.log(agas);
                submitInit(sups, 1);
                submitInit(agas, 2);
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
        } catch (e) {
            console.error(e);
            reject(e);
		}
    });
}

function runOddsCron() {
    // cron.schedule('* 1 * * * *', async function() {
    cron.schedule('*/2 * * * *', async function() {
		console.log('odds cron running a task every 1m at ' + new Date());
        try {
            const setting = await settingDAO.getByName('BotsCronJob');
            if (!setting) {
                console.log('BotsCronJob is null. Exit!');
                return;
            }
            if(!setting.status) {
                console.log('Exit BotsCronJob with status: ' + setting.status);
                return;
            }
            console.log('Begin run BotsCronJob!');

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

module.exports = { runOddsCron };
