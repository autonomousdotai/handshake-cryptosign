const cron = require('node-cron');
const moment = require('moment');
const axios = require('axios');

const configs = require('../configs');
const resource = require('../libs/utils');

// daos
const matchDAO = require('../daos/match');
const outcomeDAO = require('../daos/outcome');
const settingDAO = require('../daos/setting');

const predictionContract = require('../libs/smartcontract');
const ownerAddress = configs.network[configs.network_id].ownerAddress;

// mark as running
let isRunningCreateMarket = false;

function asyncScanOutcomeNull() {
    return new Promise(async(resolve, reject) => {
        try
        {
            const outcomes = await outcomeDAO.getOutcomesNullHID();
            if (outcomes.length > 0) {
                const nonce = await resource.getNonceFromAPI(ownerAddress, outcomes.length);
                let tasks = [];
                outcomes.forEach((outcome, index) => {
                    const task = new Promise(async(resolve, reject) => {
                        try {
                            const match = await matchDAO.getMatchById(outcome.match_id);

                            const fee = match.market_fee;
                            const closingTime = match.date - Math.floor(+moment.utc()/1000) + 90 * 60;
                            const reportTime = closingTime + (2 * 60 * 60);
                            const dispute = reportTime + (2 * 60 * 60);
                            const offchain = `cryptosign_createMarket${outcome.id}`;
                            const source = match.source;

                            predictionContract
                                .createMarketTransaction(nonce + index, fee, source, closingTime, reportTime, dispute, offchain)
                                .then((hash) => {
                                    console.log(`Create outcome_id ${outcome.id} success, hash: ${hash}`);
                                    resolve(hash);
                                })
                                .catch((e) => {
                                    console.log(`Create outcome_id ${outcome.id} fail: ${e.message}`);
                                    resolve(null);
                                });
                        } catch (e) {
                            reject(e);
                        }
                    });

                    tasks.push(task);
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
        } catch (e) {
            console.error('Create outcome err: ', e);
            reject(e);
        }
    });
}


function runCreateMarketCron() {
    cron.schedule('*/1 * * * *', async function() {
		console.log('create market cron running a task every 5m at ' + new Date());
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

module.exports = { runCreateMarketCron };
