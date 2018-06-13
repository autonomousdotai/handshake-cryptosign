
const web3 = require('../configs/web3').getWeb3();
const axios = require('axios');
const configs = require('../configs');
const outcomeDAO = require('../daos/outcome');
const smartContract = require('./smartcontract');
const oddsData = require('./dataOdds');
const ownerAddress = configs.network[configs.network_id].ownerAddress;

const genData = () => {
    const arr = [];
    oddsData.forEach( i => {
        i.outcomes.forEach(o => {
            arr.push({
                outcome_id: i.outcome_id,
                name: i.name,
                extra_data: i.extra_data,
                side: o.side,
                odds: o.odds
              });
        });
    });
    return arr;
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
                    amount: "0.01",
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
                .then(async (response) => {
                    if (response.data.status == 1 && response.data.data.length != 0) {
                        const _outcome = outcomeDAO.getById(item.outcome_id);
                        arrTnxSubmit.push({
                            hid: _outcome.hid,
                            odds: web3.utils.toWei( (parseInt(item.odds) * 100) + ''),
                            value: web3.utils.toWei(item.amount),
                            offchain: response.data.data[0].offchain,
                            side: item.side
                        });
                    } else {
                        console.log('===== ERROR =====');
                        console.log(dataRequest);
                        console.error(response.data);
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

const initHandshake = () => {
    const arr = genData();
    submitInitAPI(arr)
    .then(async tnxDataArr => {
        try {
            const results = await tnxDataArr.map(async tnx => {
                return await smartContract.submitInitTransaction();
            });
            console.log(results);
        } catch (e) {
            console.log(err);
        }
    })
    .catch(console.error);
};

module.exports = { initHandshake };
