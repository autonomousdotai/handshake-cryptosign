
const configs = require('../configs');

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

const ethTx = require('ethereumjs-tx');
const PredictionABI = require('../contracts/PredictionHandshake.json').abi;

const getNonce = async (address, status) => {
  status = status ? status : 'latest'; //pending
  return web3.eth.getTransactionCount(address, status);
}

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
        txDAO.create(tnxHash, bettingHandshakeAddress, 'init', 1, network_id, _offchain, JSON.stringify(rawTransaction))
        .catch(console.error);
        console.log(receipt);
      })
      .on('error', err => {
        txDAO.create(tnxHash, bettingHandshakeAddress, 'init', -1, network_id, _offchain, JSON.stringify(rawTransaction))
        .catch(console.error);
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
const submitInitTestDriveTransaction = (_hid, _side, _odds, _maker, _offchain, amount, _nonce) => {
  console.log('submitInitTestDriveTransaction');
  console.log(_hid, _side, _odds, _maker, _offchain, amount, _nonce);
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
          'value'   : web3.utils.toHex(web3.utils.toWei(amount + '', 'ether')),
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

// /*
//     submit shake test drive transaction
// */

const submitShakeTestDriveTransaction = (_hid, _side, _taker, _takerOdds, _maker, _makerOdss, _offchain, amount, _nonce) => {
  console.log('submitShakeTestDriveTransaction');
  console.log(_hid, _side, _taker, _takerOdds, _maker, _makerOdss, _offchain, amount, _nonce);
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
          'value'   : web3.utils.toHex(web3.utils.toWei(amount + '', 'ether')),
          'data'    : contract.methods.shakeTestDrive(_hid, _side, _taker, _takerOdds, _maker, _makerOdss, web3.utils.fromUtf8(_offchain)).encodeABI()
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
        txDAO.create(tnxHash, bettingHandshakeAddress, 'shakeTestDrive', 1, network_id, _offchain, JSON.stringify(rawTransaction))
        .catch(console.error);
        console.log(receipt);
      })
      .on('error', err => {
        txDAO.create(tnxHash, bettingHandshakeAddress, 'shakeTestDrive', -1, network_id, _offchain, JSON.stringify(rawTransaction))
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
 * @param {number} params.hid
 * @param {string} params.winner
 * @param {string} params.offchain
 */
const submitCollectTestDriveTransaction = (_hid, _winner, _offchain, _nonce) => {
  console.log('submitCollectTestDriveTransaction');
  console.log(_hid, _winner, _offchain);
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
          'value'   : '0x0',
          'data'    : contract.methods.collectTestDrive(_hid, _winner, web3.utils.fromUtf8(_offchain)).encodeABI()
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
        txDAO.create(tnxHash, bettingHandshakeAddress, 'collectTestDrive', 1, network_id, _offchain, JSON.stringify(rawTransaction))
        .catch(console.error);
        console.log(receipt);
      })
      .on('error', err => {
        txDAO.create(tnxHash, bettingHandshakeAddress, 'collectTestDrive', -1, network_id, _offchain, JSON.stringify(rawTransaction))
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
      console.log('createMarketTransaction');
      console.log(_nonce, fee, source, closingTime, reportTime, dispute, offchain);
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
          txDAO.create(tnxHash, bettingHandshakeAddress, 'createMarket', 1, network_id, _offchain, JSON.stringify(rawTransaction))
          console.log('createMarketTransactionReceipt');
          console.log(receipt);
        })
        .on('error', err => {
          txDAO.create(tnxHash, bettingHandshakeAddress, 'createMarket', -1, network_id, _offchain, JSON.stringify(rawTransaction))
          console.log(err);
          return reject(err);
        });
    } catch (e) {
      reject(e);
    }
  });
};


const reportOutcomeTransaction = (hid, outcome_result, nonce) => {
  return new Promise(async(resolve, reject) => {
    try {
      const offchain = 'cryptosign_report' + outcome_result;
      console.log('reportOutcomeTransaction');
      console.log(hid, outcome_result, offchain);

      const contractAddress = bettingHandshakeAddress;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toHex(web3.utils.toWei(gasPrice, 'gwei'));
      const contract        = new web3.eth.Contract(PredictionABI, contractAddress, {
          from: ownerAddress
      });

      const txParams = {
        gasPrice: gasPriceWei,
        gasLimit: 350000,
        to: contractAddress,
        from: ownerAddress,
        nonce: '0x' + nonce.toString(16),
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

module.exports = {
  submitInitTransaction,
  createMarketTransaction,
  submitInitTestDriveTransaction,
  getNonce,
  reportOutcomeTransaction,
  submitShakeTestDriveTransaction,
  submitCollectTestDriveTransaction
};
