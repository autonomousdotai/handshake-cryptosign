
const axios = require('axios');
const moment = require('moment');
const web3 = require('../configs/web3').getWeb3();
const web3Util = require('../configs/web3');
const configs = require('../configs');
const taskDAO = require('../daos/task');
const settingDAO = require('../daos/setting');
const constants = require('../constants');

const network_id = configs.network_id;
const predictionContract = require('../libs/smartcontract');
const amountDefaultValue = configs.network[configs.network_id].amountValue;
const ownerAddress = configs.network[network_id].ownerAddress;

const gennerateExtraData = (match_date, match_name, outcome_name) => {
    return JSON.stringify({
        event_name: match_name,
        event_predict: outcome_name,
        date: moment((match_date || 0) * 1000).format("MMM DD")
    });
};

const getGaspriceEtherscan = () => {
    return new Promise((resolve, reject) => {
        axios.get(`https://api.etherscan.io/api`, {
            timeout: 1500,
            headers: {
                'Content-Type': 'application/json'
            },
            params: {
                module: 'proxy',
                action: 'eth_gasPrice',
                apikey: '2EW75CUFS1SM3HQ3CE4QVC73JZQMNU5WTD'
            }
        })
        .then(response => {
            if (response.data && response.data.result && response.data.result != '') {
                return resolve( parseInt(web3.utils.fromWei(response.data.result, 'gwei')));
            }
            console.error({
                err_type: constants.TASK_STATUS.GAS_PRICE_ETHERSCAN_FAIL,
                error: {},
                options_data: {
                    result: response
                }
            });
            return resolve();
        })
        .catch((error) => {
            console.error({
                err_type: constants.TASK_STATUS.GAS_PRICE_ETHERSCAN_FAIL,
                error: error
            });
            return resolve();
        });
    });
}

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
            from_address: options.from_address,
            free_bet: options.is_free_bet || 0
        };

        console.log('CALL HANDSHAKE INIT API: ', dataRequest);

        axios.post(`${configs.restApiEndpoint}/handshake/init`, dataRequest, {
            headers: {
                'Content-Type': 'application/json',
                'Payload': options.payload || configs.payload,
                'UID': options.uid || configs.uid,
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
                            amount: web3.utils.toWei(`${item.amount}`),
                            offchain: item.offchain,
                            side: item.side,
                            maker: item.maker_address,
                            options_data: {
                                response: item,
                                dataRequest: dataRequest
                            }
                        }));
                    } else if (item.type == 'shake') {
                        results.push(Object.assign({
                            contract_method: options.isFreeBet ? 'shakeTestDriveTransaction' : 'shake',
                            hid: options.hid,
                            amount: web3.utils.toWei(`${item.amount}`),
                            taker: item.from_address,
                            takerOdds: parseInt(item.odds * 100),
                            maker: item.maker_address,
                            makerOdds: parseInt(item.maker_odds * 100),
                            offchain: item.offchain,
                            side: item.side,
                            options_data: {
                                response: item,
                                dataRequest: dataRequest
                            }
                        }));
                    }
                });
                console.log('RESPONSE CALL HANDSHAKE INIT API: ', JSON.stringify(results));
                return resolve(results);
            } else {
                return reject({
                    err_type: constants.TASK_STATUSINIT_CALL_API_FAIL,
                    options_data: {
                        response: response.data,
                        dataRequest: dataRequest
                    }
                });
            }
        })
        .catch((error) => {
            return reject({
                err_type: constants.TASK_STATUS.INIT_CALL_API_EXCEPTION,
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
    _arr.forEach(outcome => {
        markets.push({
			contract_method: 'createMarket',
            fee: _market_fee,
            source: _source,
            closingTime: _date - Math.floor(+moment.utc()/1000),
            reportTime: _reportTime - _date,
            disputeTime: _disputeTime - _reportTime,
            offchain: `cryptosign_createMarket${outcome.id}`
		});
    });
    return markets;
};

const handleErrorTask = (task, err_type) => {
    taskDAO.updateStatusById(task, err_type || constants.TASK_STATUS.STATUS_UNKNOW)
    .catch(console.error);
}

const calculatorGasprice = () => {
    return new Promise( async (resolve, reject) => {
        try {
            const gasSetting = await settingDAO.getByName('GasPrice');
            let gasPrice = parseInt(gasSetting.value);

            if (gasSetting.status == 0) {
                getGaspriceEtherscan()
                .then(gasAPI => {
                    if (gasPrice > gasAPI) {
                        return resolve(gasAPI);
                    }
                    return resolve(gasPrice);
                })
                .catch(ex => {
                    console.error('Etherscan gasprice error: ', ex);
                    return resolve(gasPrice);
                });
            } else {
                return resolve(gasPrice);
            }
        } catch (e) {
            return reject({
                err_type: constants.TASK_STATUS.GAS_PRICE_SETTING_FAIL,
                error: e
            });
        }
    });
}

const getGasAndNonce = () => {
	return new Promise((resolve, reject) => {
		calculatorGasprice()
		.then(gasPrice => {
			predictionContract.getNonce(ownerAddress, 'pending')
			.then(_nonce => {
				console.log('Current nonce pending from onchain: ', _nonce);
				let nonce = web3Util.getNonce();
				if (!web3Util.getNonce() || web3Util.getNonce() <= _nonce) {
					console.log('SET NONCE: ', web3Util.getNonce(), _nonce);
					web3Util.setNonce(_nonce);
					nonce = _nonce;
				}
				console.log('Current nonce pending: ', nonce);
				resolve({
					gasPriceStr: `${gasPrice}`,
					nonce: nonce
				});
			})
			.catch(err => {
				return reject(err);
			});	
		})
		.catch(err => {
			return reject(err);
		});
	});
};

/**
 * @param {JSON string} hs
 */
const addFeedAPI = (hs) => {
    return new Promise((resolve, reject) => {
        const arr = [];
        arr.push(hs);
        const dataRequest = {
            add: arr
        }

        axios.post(`${configs.solrApiEndpoint}/handshake/update`, dataRequest, {
            timeout: 1500,
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.status >= 400) {
                return reject({});
            } else {
                if (response.data.Success) {
                    return resolve({});   
                } else {
                    return reject({});
                }
            }
        })
        .catch((error) => {
            return reject(error);
        });
    });
};

module.exports = {
    submitInitAPI,
    generateMarkets,
    gennerateExtraData,
    handleErrorTask,
    calculatorGasprice,
    getGasAndNonce,
    addFeedAPI
};
