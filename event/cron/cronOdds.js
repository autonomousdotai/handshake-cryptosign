const cron = require('node-cron');
const configs = require('../configs');

// daos
const matchDAO = require('../daos/match');
const handshakeDAO = require('../daos/handshake');

const resource = require('../libs/resource')
const predictionContract = require('../libs/smartcontract');

const web3 = require('../configs/web3').getWeb3();

const ownerAddress = configs.network[configs.network_id].ownerAddress;
// mark as running
let isRunningOdds = false;

function submitInitTransactions(dataInit, total, success) {
    return new Promise(function (resolve, reject) {
        try
        {
            // const nonce = await resource.getNonceFromAPI(ownerAddress, dataInit.length);

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
        } catch (e) {
            console.error('submit InitTransactions err: ', e);
            reject(e);
        }
    });
};

function asyncScanOddsNull() {
    return new Promise(async (resolve, reject) => {
        const supports = await handshakeDAO.getSupportOddsNull();
        const againsts = await handshakeDAO.getAgainstOddsNull();

        let dataInit = [];
        const tasks = [];

        const submitInit = (arr, side) => {
            arr.forEach(item => {
                tasks.push(new Promise(async (_resolve, _reject) => {
                    const match = await matchDAO.getMatchById(item.match_id);
                    const amount = '0.1';
                    resource
                        .submitInit(item, match.toJSON(), configs.network[configs.network_id].ownerAddress, side, configs.network_id, amount)
                        .then(response => {
                            if (response.status == 1 && response.status_code == 200 && response.data.length != 0) {
                                dataInit.push({
                                    hid: item.hid,
                                    payout: web3.utils.toWei(response.data[0].odds + ""),
                                    value: web3.utils.toWei(amount),
                                    offchain: response.data[0].offchain,
                                    side: side
                                });
                            } else {
                                console.error(response);
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

function runOddsCron() {
    // cron.schedule('* 1 * * * *', async function() {
    cron.schedule('*/1 * * * *', async function() {
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

module.exports = { runOddsCron };
