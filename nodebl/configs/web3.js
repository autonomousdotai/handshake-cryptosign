
const configs = require('../configs');
const Web3 = require('web3');

const web3Provider = new Web3(new Web3.providers.HttpProvider(configs.network[configs.network_id].blockchainNetwork));

const getWeb3 = () => {
    return web3Provider;
  };
  
module.exports = { getWeb3 };