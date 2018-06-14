
const web3 = require('../configs/web3').getWeb3();
const axios = require('axios');
const configs = require('../configs');
const utils = require('../libs/utils');
const outcomeDAO = require('../daos/outcome');
const matchDAO = require('../daos/match');
const smartContract = require('./smartcontract');
const oddsData = require('./handShakeData');
const ownerAddress = configs.network[configs.network_id].ownerAddress;
const amountDefaultValue = configs.network[configs.network_id].amountValue;

const genData = (start, end) => {
    return new Promise((resolve, reject) => {
        const arr = [];
        const tasks = [];
        if (start >= end ) {
            return reject(`error: ${start} >= ${end}`);
        }
        const oddsArr = oddsData.slice(start, end);
        console.log(oddsArr);
        oddsArr.forEach( i => {
            tasks.push(new Promise((resolve, reject) => {
                matchDAO.getMatchByName(i.name)
                .then(match => {
                    if (!match) {
                        return resolve();
                    }
                    outcomeDAO.getByMatchId(match.id)
                    .then(outcome => {
                        if (!outcome) {
                            return resolve();
                        }
                        i.outcomes.forEach(o => {
                            arr.push({
                                outcome_id: outcome.id,
                                name: i.name,
                                extra_data: utils.gennerateExtraData(match, outcome),
                                side: o.side,
                                odds: o.odds
                            });
                        });
                        return resolve();
                    })
                    .catch(reject);
                })
                .catch(reject);
            }));
        });
        Promise.all(tasks)
        .then(result => {
            resolve(arr);
        })
        .catch(reject);
    });
}

const submitInitAPI = (arr) => {
    return new Promise((resolve, reject) => {
        const arrTnxSubmit = [];
        const tasks = [];
        arr.forEach(item => {
            tasks.push(new Promise((resolve, reject) => {
                const dataRequest = {
                    type: 3,
                    extra_data: item.extra_data,
                    description: 'data init',
                    outcome_id: item.outcome_id,
                    odds: item.odds,
                    amount: amountDefaultValue + '',
                    currency: 'ETH',
                    chain_id: configs.network_id,
                    side: item.side,
                    from_address: ownerAddress
                };

                axios.post(`${configs.restApiEndpoint}/handshake/init`, dataRequest, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Payload': configs.payload,
                        'UID': configs.uid,
                        'Fcm-Token': configs.fcm_token
                    }
                })
                .then(async response => {
                    if (response.data.status == 1 && response.data.data.length != 0) {
                        const _outcome = await outcomeDAO.getById(item.outcome_id);
                        arrTnxSubmit.push({
                            hid: _outcome.hid,
                            odds: parseInt(item.odds * 100),
                            value: web3.utils.toWei(dataRequest.amount),
                            offchain: response.data.data[0].offchain,
                            side: item.side
                        });
                    } else {
                        console.log('===== ERROR =====');
                        console.log(response.data);
                        console.log(dataRequest);
                    }
                    return resolve();
                })
                .catch((error) => {
                    return reject(error);
                });
            }));
        });
        Promise.all(tasks)
        .then(result => {
            resolve(arrTnxSubmit);
        })
        .catch(console.error);
    });
};

const initHandshake = async (start, end ) => {
    try {
        const arr = await genData(start, end);
        submitInitAPI(arr)
        .then(async tnxDataArr => {
            const nonce = await smartContract.getNonce(ownerAddress);
            const tasks = [];
            
            tnxDataArr.forEach((tnx, index) => {
                tasks.push(new Promise((resolve, reject) => {
                    smartContract.submitInitTransaction(nonce + index, tnx.hid, tnx.side, tnx.odds, tnx.offchain, tnx.value)
                    .then(result => {
                        console.log(result);
                        resolve();
                    })
                    .catch(err => {
                        console.error(err);
                        reject(err);
                    });
                }));
            });
            Promise.all(tasks)
            .then()
            .catch(console.error)
        })
        .catch(console.error);
    } catch (e) {
        console.log(e);
    }
};

module.exports = { initHandshake };

