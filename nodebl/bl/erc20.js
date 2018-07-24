const configs = require('../configs');
const network_id = configs.network_id;

predictionContractWithTokenName = 'PredictionHandshakeWithToken';
predictionContractWithTokenAddress = configs.network[network_id].bettingHandshakeWithTokenAddress;


/**
 * 
 * @param {string} params.tokenAddress
 * @param {string} params.offchain
 */
const approveNewToken = (params) => {
	return new Promise((resolve, reject) => {
		return resolve([{
            contract_name: predictionContractWithTokenName,
            contract_method: 'approveNewToken',
            contract_address: predictionContractWithTokenAddress,
			tokenAddress: params.tokenAddress,
			offchain: params.offchain
		}])
	});
};

module.exports = {
    approveNewToken
};