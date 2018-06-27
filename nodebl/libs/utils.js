
const axios = require('axios');
const moment = require('moment');
const web3 = require('../configs/web3').getWeb3();
const configs = require('../configs');
const network_id = configs.network_id;
const ownerAddress = configs.network[network_id].ownerAddress;
const amountDefaultValue = configs.network[configs.network_id].amountValue;
const reportTimeConfig = configs.network[configs.network_id].reportTimeConfig || 2;

const gennerateExtraData = (match_date, match_name, outcome_name) => {
    return JSON.stringify({
        event_name: match_name,
        event_predict: outcome_name,
        date: moment((match_date || 0) * 1000).format("MMM DD")
    });
};

/**
 * 
 * @param {number} options.type
 * @param {JSON string} options.extra_data
 * @param {number} options.outcome_id
 * @param {number} options.odds
 * @param {number} options.amount
 * @param {string} options.currency
 * @param {number} options.side
 * @param {string} options.from_address
 * @param {boolean} options.isFreeBet
 */
const submitInitAPI = (options) => {
    return new Promise((resolve, reject) => {
        const dataRequest = {
            type: options.type,
            extra_data: options.extra_data,
            description: 'init from task cron',
            outcome_id: options.outcome_id,
            odds: options.odds,
            amount: (options.amount || amountDefaultValue) + '',
            currency: options.currency,
            chain_id: network_id,
            side: options.side,
            from_address: ownerAddress
        };

        console.log('CALL HANDSHAKE INIT API: ', dataRequest);

        axios.post(`${configs.restApiEndpoint}/handshake/init`, dataRequest, {
            headers: {
                'Content-Type': 'application/json',
                'Payload': configs.payload,
                'UID': configs.uid,
                'Fcm-Token': configs.fcm_token
            }
        })
        .then(response => {
            if (response.data.status == 1 && response.data.data.length != 0) {
                const results = [];
                response.data.data.forEach(item => {
                    if (item.type == 'init') {
                        results.push(Object.assign({
                            contract_method: options.isFreeBet ? 'initTestDriveTransaction' : 'init',
                            hid: options.hid,
                            odds: parseInt(item.odds * 100),
                            value: web3.utils.toWei(`${item.amount}`), //TODO: check
                            offchain: item.offchain,
                            side: item.side,
                            options_data: {
                                response: item,
                                dataRequest: dataRequest
                            }
                        }));
                    } else if (item.type == 'shake') {
                        results.push(Object.assign({
                            contract_method: options.isFreeBet ? 'shakeTestDriveTransaction' : 'shake',
                            hid: options.hid,
                            odds: parseInt(item.odds * 100),
                            amount: web3.utils.toWei(`${item.amount}`), //TODO: check
                            maker: item.maker_address,
                            offchain: item.offchain,
                            side: item.side,
                            options_data: {
                                response: item,
                                dataRequest: dataRequest
                            }
                        }));
                    }
                });
                console.log('RESPONSE CALL HANDSHAKE INIT API: ', results);
                return resolve(results);
            } else {
                return reject({
                    err_type: 'INIT_CALL_API_FAIL',
                    options_data: {
                        response: response.data,
                        dataRequest: dataRequest
                    }
                });
            }
        })
        .catch((error) => {
            return reject({
                err_type: 'INIT_CALL_API_EXCEPTION',
                error: error,
                options_data: {
                    dataRequest: dataRequest
                }
            });
        });
    });
};


/* @param {number} result
 * @param {number} public
 * @param {number} hid
 * @param {string} name
 */
const generateMarkets = (_arr, _market_fee, _date, _disputeTime, _reportTime, _source ) => {
    const markets = [];
    const closingTime = _date - Math.floor(+moment.utc()/1000) + 90 * 60 + 15 * 60;

    let reportTime = closingTime + (reportTimeConfig * 60 * 60);
    if (_reportTime) {
        reportTime = _reportTime - Math.floor(+moment.utc()/1000);
    }

    let dispute = reportTime + (reportTimeConfig * 60 * 60);
    if (_disputeTime) {
        dispute = _disputeTime - Math.floor(+moment.utc()/1000);
    }

    _arr.forEach(outcome => {
        markets.push({
			contract_method: 'createMarket',
            fee: _market_fee,
            source: _source,
            closingTime: closingTime,
            reportTime: reportTime,
            disputeTime: dispute,
            offchain: `cryptosign_createMarket${outcome.id}`
		});
    });
    return markets;
};

module.exports = {
    submitInitAPI,
    generateMarkets,
    gennerateExtraData
};
