const configs = require('../configs');
const network_id = configs.network_id;

tokenRegistryContractName = 'TokenRegistry';
tokenRegistryContractAddress = configs.network[network_id].tokenRegistryAddress;

                                        
/**
 * 
 * @param {number} params.decimal
 * @param {string} params.symbol
 * @param {string} params.name
 * @param {string} params.contract_address
 * @param {string} params.offchain
 */
const addToken = (params) => {
	return new Promise((resolve, reject) => {
		return resolve([{
            contract_name: tokenRegistryContractName,
            contract_method: 'addNewToken',
            contract_address: tokenRegistryContractAddress,
			decimals: params.decimal,
			symbol: params.symbol,
            name: params.name,
            token_address: params.contract_address,
			offchain: params.offchain
		}])
	});
};

module.exports = {
    addToken
};