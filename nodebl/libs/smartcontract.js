
const configs = require('../configs');
const constants = require('../constants');
// models
const txDAO = require('../daos/tx');
const web3 = require('../configs/web3').getWeb3();
const web3Config = require('../configs/web3');

const network_id = configs.network_id;
const bettingHandshakeAddress = configs.network[network_id].bettingHandshakeAddress;
const ownerAddress = configs.network[network_id].ownerAddress;
const privateKey = configs.network[network_id].privateKey;
const gasLimit = configs.network[network_id].gasLimit;

const ethTx = require('ethereumjs-tx');
const PredictionABI = require('../contracts/PredictionHandshake.json').abi;

const getNonce = async (address, status) => {
  status = status ? status : 'latest'; //pending
  return web3.eth.getTransactionCount(address, status);
}

// /*
//     submit init transaction
// */
const submitInitTransaction = (_nonce, _hid, _side, _odds, _offchain, _value, gasPrice, _options) => {
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

        txDAO.create(tnxHash, bettingHandshakeAddress, 'init', -1, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { _options })))
        .catch(console.error);

        return resolve({
          raw: rawTransaction,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
        console.log(receipt);
      })
      .on('error', err => {
        console.log('submitInitTransaction Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, bettingHandshakeAddress, 'init', 0, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })))
          .catch(console.error);
        } else {
          web3Config.setNonce(web3Config.getNonce() -1);
        }
        return reject({
          err_type: constants.TASK_STATUS.INIT_TNX_FAIL,
          error: err,
          options_data: {
            task: _options.task
          }
        });
      });
    } catch (e) {
      reject({
        err_type: constants.TASK_STATUS.INIT_TNX_EXCEPTION,
        error: e,
        options_data: {
          task: _options.task
        }
      });
    }
  });
};

// /*
//     submit init test drive transaction
// */
const submitInitTestDriveTransaction = (_hid, _side, _odds, _maker, _offchain, amount, _nonce, gasPrice, _options) => {
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
          // 'value'   : web3.utils.toHex(web3.utils.toWei(amount + '', 'ether')),
          'value'   : web3.utils.toHex(amount),
          'data'    : contract.methods.initTestDrive(_hid, _side, _odds, _maker, web3.utils.fromUtf8(_offchain)).encodeABI()
      };
      const tx                    = new ethTx(rawTransaction);
      tx.sign(privKey);
      const serializedTx          = tx.serialize();
      let tnxHash                 = -1;
      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, bettingHandshakeAddress, 'initTestDrive', -1, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { _options })))
        .catch(console.error);

        return resolve({
          raw: rawTransaction,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
        console.log(receipt);
      })
      .on('error', err => {
        console.log('submitInitTestDriveTransaction Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, bettingHandshakeAddress, 'initTestDrive', 0, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })))
          .catch(console.error);
        } else {
          web3Config.setNonce(web3Config.getNonce() -1);
        }
        return reject({
          err_type: constants.TASK_STATUS.INIT_TEST_DRIVE_TNX_FAIL,
          error: err,
          options_data: {
            task: _options.task
          }
        });
      });
    } catch (e) {
      console.error(e);
      reject({
        err_type: constants.TASK_STATUS.INIT_TEST_DRIVE_TNX_EXCEPTION,
        error: e,
        options_data: {
          task: _options.task
        }
      });
    }
  });
};


// /*
//     submit shake transaction
// */
const submitShakeTransaction = (_hid, _side, _taker, _takerOdds, _maker, _makerOdds, _offchain, amount, _nonce, gasPrice, _options) => {
  console.log('submitShakeTransaction');
  console.log(_hid, _side, _taker, _takerOdds, _maker, _makerOdds, _offchain, amount, _nonce);
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
          // 'value'   : web3.utils.toHex(amount),
          'data'    : contract.methods.shake(_hid, _side, _takerOdds, _maker, _makerOdds, web3.utils.fromUtf8(_offchain)).encodeABI()
      };
      const tx                    = new ethTx(rawTransaction);
      tx.sign(privKey);
      const serializedTx          = tx.serialize();
      let tnxHash                 = -1;
      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, bettingHandshakeAddress, 'shake', -1, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { _options })))
        .catch(console.error);

        return resolve({
          raw: rawTransaction,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
        console.log(receipt);
      })
      .on('error', err => {
        console.log('submitShakeTransaction Error');
        console.log(err);

        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, bettingHandshakeAddress, 'shake', 0, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })))
          .catch(console.error);
        } else {
          web3Config.setNonce(web3Config.getNonce() -1);
        }
        return reject({
          err_type: constants.TASK_STATUS.SHAKE_TNX_FAIL,
          error: err,
          options_data: {
            task: _options.task
          }
        });
      });
    } catch (e) {
      console.error(e);
      reject({
        err_type: constants.TASK_STATUS.SHAKE_TNX_EXCEPTION,
        error: e,
        options_data: {
          task: _options.task
        }
      });
    }
  });
};


// /*
//     submit shake test drive transaction
// */
const submitShakeTestDriveTransaction = (_hid, _side, _taker, _takerOdds, _maker, _makerOdds, _offchain, amount, _nonce, gasPrice, _options) => {
  console.log('submitShakeTestDriveTransaction');
  console.log(_hid, _side, _taker, _takerOdds, _maker, _makerOdds, _offchain, amount, _nonce);
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
          // 'value'   : web3.utils.toHex(web3.utils.toWei(amount + '', 'ether')),
          'value'   : web3.utils.toHex(amount),
          'data'    : contract.methods.shakeTestDrive(_hid, _side, _taker, _takerOdds, _maker, _makerOdds, web3.utils.fromUtf8(_offchain)).encodeABI()
      };

      const tx                    = new ethTx(rawTransaction);
      tx.sign(privKey);
      const serializedTx          = tx.serialize();
      let tnxHash                 = -1;
      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, bettingHandshakeAddress, 'shakeTestDrive', -1, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { _options })))
        .catch(console.error);

        return resolve({
          raw: rawTransaction,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
        console.log(receipt);
      })
      .on('error', err => {
        console.log('submitShakeTestDriveTransaction Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, bettingHandshakeAddress, 'shakeTestDrive', 0, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })))
          .catch(console.error);
        } else {
          web3Config.setNonce(web3Config.getNonce() -1);
        }
        return reject({
          err_type: constants.TASK_STATUS.SHAKE_TEST_DRIVE_TNX_FAIL,
          error: err,
          options_data: {
            task: _options.task
          }
        });
      });
    } catch (e) {
      console.error(e);
      reject({
        err_type: constants.TASK_STATUS.SHAKE_TEST_DRIVE_TNX_EXCEPTION,
        error: e,
        options_data: {
          task: _options.task
        }
      });
    }
  });
};

/**
 * @param {number} params.hid
 * @param {string} params.winner
 * @param {string} params.offchain
 */
const submitCollectTestDriveTransaction = (_hid, _winner, _offchain, _nonce, gasPrice, _options) => {
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

        txDAO.create(tnxHash, bettingHandshakeAddress, 'collectTestDrive', -1, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { _options })))
        .catch(console.error);

        return resolve({
          raw: rawTransaction,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
        console.log(receipt);
      })
      .on('error', err => {
        console.log('submitCollectTestDriveTransaction Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, bettingHandshakeAddress, 'collectTestDrive', 0, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })))
          .catch(console.error);
        } else {
          web3Config.setNonce(web3Config.getNonce() -1);
        }
        return reject({
          err_type: constants.TASK_STATUS.COLLECT_TEST_DRIVE_TNX_FAIL,
          error: err,
          options_data: {
            task: _options.task
          }
        });
      });
    } catch (e) {
      console.error(e);
      reject({
        err_type: constants.TASK_STATUS.COLLECT_TEST_DRIVE_TNX_EXCEPTION,
        error: e,
        options_data: {
          task: _options.task
        }
      });
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

const createMarketTransaction = (_nonce, fee, source, closingTime, reportTime, dispute, offchain, gasPrice, _options) => {
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
      let tnxHash = -1;

      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, bettingHandshakeAddress, 'createMarket', -1, network_id, offchain, JSON.stringify(Object.assign(rawTransaction, { _options })))
        .catch(console.error);

        return resolve({
          raw: rawTransaction,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
        console.log('createMarketTransactionReceipt');
        console.log(receipt);
      })
      .on('error', err => {
        console.log('createMarketTransaction Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, bettingHandshakeAddress, 'createMarket', 0, network_id, offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })))
          .catch(console.error);
        } else {
          web3Config.setNonce(web3Config.getNonce() -1);
        }
        return reject({
          err_type: constants.TASK_STATUS.CREATE_MARKET_TNX_FAIL,
          error: err,
          options_data: {
            task: _options.task
          }
        });
      });
    } catch (e) {
      reject({
        err_type: constants.TASK_STATUS.CREATE_MARKET_TNX_EXCEPTION,
        error: e,
        options_data: {
          task: _options.task
        }
      });
    }
  });
};


const reportOutcomeTransaction = (hid, outcome_result, nonce, _offchain, gasPrice, _options) => {
  return new Promise(async(resolve, reject) => {
    try {
      const offchain = _offchain || ('cryptosign_report' + outcome_result);
      console.log('reportOutcomeTransaction');
      console.log(hid, outcome_result, nonce, _offchain, gasPrice);

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

        txDAO.create(tnxHash, bettingHandshakeAddress, 'report', -1, network_id, _offchain, JSON.stringify(Object.assign(txParams, { _options })))
        .catch(console.error);

        return resolve({
          raw: txParams,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
        console.log('report tnxHash: ', receipt);
      })
      .on('error', err => {
        console.log('reportOutcomeTransaction Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, bettingHandshakeAddress, 'report', 0, network_id, _offchain, JSON.stringify(Object.assign(txParams, { err: err.message, _options, tnxHash })))
          .catch(console.error);
        } else {
          web3Config.setNonce(web3Config.getNonce() -1);
        }
        return reject({
          err_type: constants.TASK_STATUS.REPORT_TNX_FAIL,
          error: err,
          options_data: {
            task: _options.task
          }
        });
      });
    } catch (e) {
      reject({
        err_type: constants.TASK_STATUS.REPORT_TNX_EXCEPTION,
        error: e,
        options_data: {
          task: _options.task
        }
      });
    }
  });
};

const uninitForTrial = (_hid, _side, _odds, _maker, _value, _offchain, _nonce, gasPrice, _options) => {
  return new Promise(async(resolve, reject) => {
    try {
      console.log('uninitForTrial');
      console.log(_hid, _side, _odds, _maker, _value, _nonce, _offchain, _options);

      const contractAddress = bettingHandshakeAddress;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toHex(web3.utils.toWei(gasPrice, 'gwei'));
      const value           = web3.utils.toHex(web3.utils.toWei(_value));
      const contract        = new web3.eth.Contract(PredictionABI, contractAddress, {
          from: ownerAddress
      });

      const txParams = {
        gasPrice: gasPriceWei,
        gasLimit: 350000,
        to: contractAddress,
        from: ownerAddress,
        nonce: '0x' + _nonce.toString(16),
        chainId: network_id,
        data: contract.methods.uninitTestDrive(_hid, _side, _odds, _maker, value, web3.utils.fromUtf8(_offchain)).encodeABI()
      };

      const tx = new ethTx(txParams);
      let tnxHash = -1;
      tx.sign(privKey);

      const serializedTx = tx.serialize();

      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, bettingHandshakeAddress, 'uninitForTrial', -1, network_id, _offchain, JSON.stringify(Object.assign(txParams, { _options })))
        .catch(console.error);

        return resolve({
          raw: txParams,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
        console.log('uninitForTrial tnxHash: ', receipt);
      })
      .on('error', err => {
        console.log('uninitForTrial Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, bettingHandshakeAddress, 'uninitForTrial', 0, network_id, _offchain, JSON.stringify(Object.assign(txParams, { err: err.message, _options, tnxHash })))
          .catch(console.error);
        } else {
          web3Config.setNonce(web3Config.getNonce() -1);
        }
        return reject({
          err_type: constants.TASK_STATUS.UNINIT_FOR_TRIAL_TNX_FAIL,
          error: err,
          options_data: {
            task: _options.task
          }
        });
      });
    } catch (e) {
      reject({
        err_type: constants.TASK_STATUS.UNINIT_FOR_TRIAL_TNX_EXCEPTION,
        error: e,
        options_data: {
          task: _options.task
        }
      });
    }
  });
};

module.exports = {
  submitInitTransaction,
  createMarketTransaction,
  submitInitTestDriveTransaction,
  getNonce,
  reportOutcomeTransaction,
  submitShakeTransaction,
  submitShakeTestDriveTransaction,
  submitCollectTestDriveTransaction,
  uninitForTrial
};
