const cron = require('node-cron');

const configs = require('../configs');
const moment = require('moment');

// daos
const matchDAO = require('../daos/match');
const outcomeDAO = require('../daos/outcome');

const predictionContract = require('../libs/smartcontract');

// mark as running
let isRunningCreateMarket = false;


function asyncScanOutcomeNull() {
    return new Promise(async(resolve, reject) => {
        try
        {
            const outcomes = await outcomeDAO.getOutcomesNullHID();
            if (outcomes.length > 0) {
                let tasks = [];
                outcomes.forEach((outcome, index) => {
                    const task = new Promise(async(resolve, reject) => {
                        try {
                            const match = await matchDAO.getMatchById(outcome.match_id);

                            const fee = match.market_fee;
                            const closingTime = match.date - Math.floor(+moment.utc()/1000);
                            const reportTime = closingTime + (4 * 60 * 60);
                            const dispute = reportTime + (4 * 60 * 60);
                            const offchain = `cryptosign_createMarket${outcome.id}`;
                            const source = match.source;

                            predictionContract
                                .createMarketTransaction(index, fee, source, closingTime, reportTime, dispute, offchain)
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

module.exports = { runCreateMarketCron };
