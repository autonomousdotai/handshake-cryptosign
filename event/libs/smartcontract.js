
const Web3 = require('web3');
const configs = require('../configs');
const httpRequest = require('../libs/http');
const PredictionHandshake = require('../contracts/PredictionHandshake.json');
const axios = require('axios');

const network_id = configs.network_id;
const web3 = new Web3(new Web3.providers.HttpProvider(configs.network[network_id].blockchainNetwork));
const bettingHandshakeAddress = configs.network[network_id].bettingHandshakeAddress;
const ownerAddress = configs.network[network_id].ownerAddress;
const privateKey = configs.network[network_id].privateKey;
const gasLimit = configs.network[network_id].gasLimit;

const contractPredictionHandshake = new web3.eth.Contract(PredictionHandshake.abi, bettingHandshakeAddress);

const ethTx = require('ethereumjs-tx');
const PredictionABI = require('../contracts/PredictionHandshake.json').abi;

const padLeftEven = (hex) => {
  hex = hex.length % 2 !== 0 ? '0' + hex : hex;
  return hex;
};

const padLeft = (n, width, z) => {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
};

const padRight = (n, width, z) => {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : n + new Array(width - n.length + 1).join(z);
};

const stringToHex = (_str) => {
  let str = '';
  for (let i = 0; i < _str.length; i++) {
    str += _str[i].charCodeAt(0).toString(16);
  }
  return str;
};

const getNaked = (address) => {
  return address.toLowerCase().replace('0x', '');
};

const isAddress = (address) => {
  if (!/^(0x|0X)?[a-fA-F0-9]+$/.test(address)) {
    return false;
  }
  return web3.utils.isAddress(address);
};

const IsNumberUppercaseString = (string) => {
  return (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/).test(string);
};

const sanitizeHex = (hex) => {
  hex = hex.substring(0, 2) === '0x' ? hex.substring(2) : hex;
  if (hex === '') {
    return '';
  }
  return '0x' + padLeftEven(hex);
};

const getNonce = async (address, status) => {
  status = status ? status : 'latest';
  return web3.eth.getTransactionCount(address, status);
}

const getNonceFromAPI = (index, address, status) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      /*
      axios.get(`${configs.restApiEndpoint}/nonce/get?address=${address}&network_id=${network_id}`, {
      headers: {
          'Content-Type': 'application/json',
      }
      })
      .then(response => {
        if (response.data && response.data.status == 1) {
          return resolve(response.data);
        } else {
          return reject('Cannot get Nonce.');
        }
      })
      .catch(e => {
        console.log(e);
        return reject(e);
      });
      */
      getNonce(address).then(resolve).catch(reject);
    }, (index + 1) * 20000);
  });
};

const getGasPrice = async () => {
  return await web3.eth.getGasPrice();
};

// /*
//     submit init transaction
// */
const submitInitTransaction = (_index, _hid, _side, _payout, _offchain, _value) => {
  return new Promise(async(resolve, reject) => {
    try {
      const contractAddress = bettingHandshakeAddress;
      const privKey         = Buffer.from(privateKey, 'hex');
      const nonce           = await getNonceFromAPI(_index, ownerAddress);
      const gasPriceWei     = web3.utils.toWei('100', 'gwei');
      const contract        = new web3.eth.Contract(PredictionABI, contractAddress, {
          from: ownerAddress
      });
      const rawTransaction = {
          'from'    : ownerAddress,
          'nonce'   : '0x' + nonce.toString(16),
          'gasPrice': web3.utils.toHex(gasPriceWei),
          'gasLimit': web3.utils.toHex(gasLimit),
          'to'      : contractAddress,
          'value'   : web3.utils.toHex(_value),
          'data'    : contract.methods.init(1, 1, 1000, web3.utils.fromUtf8(_offchain)).encodeABI()
      };
      const tx                    = new ethTx(rawTransaction);
      tx.sign(privKey);
      const serializedTx          = tx.serialize();

      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        return resolve({
          raw: rawTransaction,
          hash: hash,
        });
      })
      .on('receipt', (receipt) => {
        console.log(receipt);
      })
      .on('error', err => {
        console.log(err);
        return reject(err);
      });
    } catch (e) {
      reject(e);
    }
  });
};

/**
 * Create Market
 * 
  uint fee, 
  bytes32 source,
  uint closingWindow, 
  uint reportWindow, 
  uint disputeWindow,
  bytes32 offchain
 */

const createMarketTransaction = (index, fee, source, closingTime, reportTime, dispute, offchain) => {
  return new Promise(async(resolve, reject) => {
    try {
      const contractAddress = bettingHandshakeAddress;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toWei('100', 'gwei');
      const nonce           = await getNonceFromAPI(index, ownerAddress);
      const contract        = new web3.eth.Contract(PredictionABI, contractAddress, {
          from: ownerAddress
      });

      const rawTransaction = {
          'from'    : ownerAddress,
          'nonce'   : '0x' + nonce.toString(16),
          'gasPrice': web3.utils.toHex(gasPriceWei),
          'gasLimit': web3.utils.toHex(gasLimit),
          'to'      : contractAddress,
          'value'   : '0x0',
          'data'    : contract.methods.createMarket(fee, web3.utils.fromUtf8(source), closingTime, reportTime, dispute, web3.utils.fromUtf8(offchain)).encodeABI()
      };

      const tx                    = new ethTx(rawTransaction);
      tx.sign(privKey);
      const serializedTx          = tx.serialize();

      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
        .on('transactionHash', (hash) => {
          return resolve(hash);
        })
        .on('receipt', (receipt) => {
        })
        .on('error', err => {
          console.log(err);
          return reject(err);
        });
    } catch (e) {
      reject(e);
    }
  });
};

module.exports = { submitInitTransaction, createMarketTransaction };
