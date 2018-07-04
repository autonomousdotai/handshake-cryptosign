
const configs = require('../configs');
const Web3 = require('web3');

const currentNonce = 0;
const web3Provider = new Web3(new Web3.providers.HttpProvider(configs.network[configs.network_id].blockchainNetwork));

const getWeb3 = () => {
  return web3Provider;
};

const getNonce = () => {
  return currentNonce;
};

const setNonce = (value) => {
  currentNonce = value;
};

module.exports = {
  getWeb3,
  getNonce,
  setNonce
};
