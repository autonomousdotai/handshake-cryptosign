
const configs = require('../configs');
const httpRequest = require('../libs/http');
const PredictionHandshake = require('../contracts/PredictionHandshake.json');
const axios = require('axios');
// models
const models = require('../models');
const txDAO = require('../daos/tx');

const web3 = require('../configs/web3').getWeb3();

const network_id = configs.network_id;
const bettingHandshakeAddress = configs.network[network_id].bettingHandshakeAddress;
const ownerAddress = configs.network[network_id].ownerAddress;
const privateKey = configs.network[network_id].privateKey;
const gasLimit = configs.network[network_id].gasLimit;
const gasPrice = `${configs.network[network_id].gasPrice}`;

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

const getGasPrice = async () => {
  return await web3.eth.getGasPrice();
};

// /*
//     submit init transaction
// */
const submitInitTransaction = (_nonce, _hid, _side, _odds, _offchain, _value) => {
  console.log('submitInitTransaction');
  console.log(_nonce, _hid, _side, _odds, _offchain, _value);
  return new Promise(async(resolve, reject) => {
    try {
      const contractAddress = bettingHandshakeAddress;
      const privKey         = Buffer.from(privateKey, 'hex');
      const nonce           = _nonce;
      const gasPriceWei     = web3.utils.toWei(gasPrice, 'gwei');
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
          'data'    : contract.methods.init(_hid, _side, _odds, web3.utils.fromUtf8(_offchain)).encodeABI()
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

// /*
//     submit init test drive transaction
// */
const submitInitTestDriveTransaction = (_hid, _side, _odds, _maker, _offchain) => {
  return new Promise(async(resolve, reject) => {
    try {
      const contractAddress = bettingHandshakeAddress;
      const privKey         = Buffer.from(privateKey, 'hex');
      const nonce           = await getNonce(ownerAddress);
      const gasPriceWei     = web3.utils.toWei(gasPrice, 'gwei');
      const contract        = new web3.eth.Contract(PredictionABI, contractAddress, {
          from: ownerAddress
      });
      const rawTransaction = {
          'from'    : ownerAddress,
          'nonce'   : '0x' + nonce.toString(16),
          'gasPrice': web3.utils.toHex(gasPriceWei),
          'gasLimit': web3.utils.toHex(gasLimit),
          'to'      : contractAddress,
          'value'   : web3.utils.toHex(web3.utils.toWei('0.001', 'ether')),
          'data'    : contract.methods.initTestDrive(_hid, _side, _odds, _maker, web3.utils.fromUtf8(_offchain)).encodeABI()
      };
      const tx                    = new ethTx(rawTransaction);
      tx.sign(privKey);
      const serializedTx          = tx.serialize();
      let tnxHash                 = -1;
      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;
        return resolve({
          raw: rawTransaction,
          hash: hash,
        });
      })
      .on('receipt', (receipt) => {
        txDAO.create(tnxHash, bettingHandshakeAddress, 'initTestDrive', 1, network_id, _offchain, JSON.stringify(rawTransaction))
        .catch(console.error);
        console.log(receipt);
      })
      .on('error', err => {
        txDAO.create(tnxHash, bettingHandshakeAddress, 'initTestDrive', -1, network_id, _offchain, JSON.stringify(rawTransaction))
        .catch(console.error);
        console.log(err);
        return reject(err);
      });
    } catch (e) {
      console.error(e);
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

const createMarketTransaction = (_nonce, fee, source, closingTime, reportTime, dispute, offchain) => {
  return new Promise(async(resolve, reject) => {
    try {
      const contractAddress = bettingHandshakeAddress;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toWei(gasPrice, 'gwei');
      const nonce           = _nonce;
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
          console.log('nonce: ', _nonce);
          console.log(rawTransaction);
          return resolve(hash);
        })
        .on('receipt', (receipt) => {
          console.log('createMarketTransactionReceipt');
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


const reportOutcomeTransaction = (hid, outcome_result) => {
  return new Promise(async(resolve, reject) => {
    try {
      const offchain = 'cryptosign_report' + outcome_result;
      console.log('reportOutcomeTransaction');
      console.log(hid, outcome_result, offchain);

      const contractAddress = bettingHandshakeAddress;
      const privKey         = Buffer.from(privateKey, 'hex');
      let nonce             = await getNonce(ownerAddress);
      nonce                 = nonce.toString(16)
      const gasPriceWei     = web3.utils.toHex(web3.utils.toWei(gasPrice, 'gwei'));
      const contract        = new web3.eth.Contract(PredictionABI, contractAddress, {
          from: ownerAddress
      });

      const txParams = {
        gasPrice: gasPriceWei,
        gasLimit: 350000,
        to: contractAddress,
        from: ownerAddress,
        nonce: '0x' + nonce,
        chainId: network_id,
        data: contract.methods.report(hid, outcome_result, web3.utils.fromUtf8(offchain)).encodeABI()
      };

      const tx = new ethTx(txParams);
      let tnxHash = -1;
      tx.sign(privKey);

      const serializedTx = tx.serialize();

      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;
        console.log('report tnxHash: ', hash);
      })
      .on('receipt', (receipt) => {
        console.log('report tnxHash: ', receipt);
        txDAO.create(tnxHash, bettingHandshakeAddress, 'report', 1, network_id, offchain, JSON.stringify(txParams))
        .catch(console.error);
        resolve(receipt);
      })
      .on('error', err => {
        txDAO.create(tnxHash, bettingHandshakeAddress, 'report', -1, network_id, offchain, JSON.stringify(txParams))
        .catch(console.error);
        console.log(err);
        reject(err);
      });
    } catch (e) {
      reject(e);
    }
  });
};

module.exports = { submitInitTransaction, createMarketTransaction, submitInitTestDriveTransaction, getNonce, reportOutcomeTransaction };
