const configs = require('../configs');


/**
 * 
 * @param {number} params.decimals
 * @param {string} params.symbol
 * @param {string} params.name
 * @param {string} params.contract_address
 * @param {string} params.offchain
 */
const addToken = (params) => {
    console.log(params);
	return new Promise((resolve, reject) => {
		return resolve([{
			contract_method: 'uninitForTrial',
			decimals: params.decimals,
			symbol: params.symbol,
            name: params.name,
            contract_address: params.contract_address,
			offchain: params.offchain
		}])
	});
};

module.exports = {
    addToken
};