
const configs = require('../configs');
const constants = require('../constants');
// models
const txDAO = require('../daos/tx');
const web3 = require('../configs/web3').getWeb3();
const web3Config = require('../configs/web3');

const network_id = configs.network_id;
const ownerAddress = configs.network[network_id].ownerAddress;
const privateKey = configs.network[network_id].privateKey;
const gasLimit = configs.network[network_id].gasLimit;

const ethTx = require('ethereumjs-tx');

const getNonce = async (address, status) => {
  status = status ? status : 'latest'; //pending
  return web3.eth.getTransactionCount(address, status);
}

const loadABI = (contract_json) => {
  const PredictionABI = require(`../contracts/${contract_json}.json`).abi;
  return PredictionABI;
}

// /*
//     submit init transaction
// */
const submitInitTransaction = (_nonce, _hid, _side, _odds, _offchain, _value, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  return new Promise(async(resolve, reject) => {
    try {
      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const nonce           = _nonce;
      const gasPriceWei     = web3.utils.toWei(gasPrice, 'gwei');
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
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

        txDAO.create(tnxHash, contract_address, 'init', -1, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { _options })), on_chain_task_id)
        .catch(console.error);

        return resolve({
          raw: rawTransaction,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
      })
      .on('error', err => {
        console.log('submitInitTransaction Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, contract_address, 'init', 0, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at submitInitTransaction');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
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
const submitInitTestDriveTransaction = (_hid, _side, _odds, _maker, _offchain, amount, _nonce, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  console.log('submitInitTestDriveTransaction');
  console.log(_hid, _side, _odds, _maker, _offchain, amount, _nonce, contract_address, contract_json);
  return new Promise(async(resolve, reject) => {
    try {
      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const nonce           = _nonce;
      const gasPriceWei     = web3.utils.toWei(gasPrice, 'gwei');
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
          from: ownerAddress
      });
      const rawTransaction = {
          'from'    : ownerAddress,
          'nonce'   : '0x' + nonce.toString(16),
          'gasPrice': web3.utils.toHex(gasPriceWei),
          'gasLimit': web3.utils.toHex(gasLimit),
          'to'      : contractAddress,
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

        txDAO.create(tnxHash, contract_address, 'initTestDrive', -1, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { _options })), on_chain_task_id)
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
          txDAO.create(-1, contract_address, 'initTestDrive', 0, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at submitInitTestDriveTransaction');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
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
const submitShakeTransaction = (_hid, _side, _taker, _takerOdds, _maker, _makerOdds, _offchain, amount, _nonce, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  console.log('submitShakeTransaction');
  console.log(_hid, _side, _taker, _takerOdds, _maker, _makerOdds, _offchain, amount, _nonce, contract_address, contract_json);
  return new Promise(async(resolve, reject) => {
    try {
      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const nonce           = _nonce;
      const gasPriceWei     = web3.utils.toWei(gasPrice, 'gwei');
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
          from: ownerAddress
      });
      const rawTransaction = {
          'from'    : ownerAddress,
          'nonce'   : '0x' + nonce.toString(16),
          'gasPrice': web3.utils.toHex(gasPriceWei),
          'gasLimit': web3.utils.toHex(gasLimit),
          'to'      : contractAddress,
          'value'   : web3.utils.toHex(amount),
          'data'    : contract.methods.shake(_hid, _side, _takerOdds, _maker, _makerOdds, web3.utils.fromUtf8(_offchain)).encodeABI()
      };
      const tx                    = new ethTx(rawTransaction);
      tx.sign(privKey);
      const serializedTx          = tx.serialize();
      let tnxHash                 = -1;
      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, contract_address, 'shake', -1, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { _options })), on_chain_task_id)
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
          txDAO.create(-1, contract_address, 'shake', 0, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at submitShakeTransaction');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
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
const submitShakeTestDriveTransaction = (_hid, _side, _taker, _takerOdds, _maker, _makerOdds, _offchain, amount, _nonce, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  console.log('submitShakeTestDriveTransaction');
  console.log(_hid, _side, _taker, _takerOdds, _maker, _makerOdds, _offchain, amount, _nonce, contract_address, contract_json);
  return new Promise(async(resolve, reject) => {
    try {
      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const nonce           = _nonce;
      const gasPriceWei     = web3.utils.toWei(gasPrice, 'gwei');
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
          from: ownerAddress
      });
      const rawTransaction = {
          'from'    : ownerAddress,
          'nonce'   : '0x' + nonce.toString(16),
          'gasPrice': web3.utils.toHex(gasPriceWei),
          'gasLimit': web3.utils.toHex(gasLimit),
          'to'      : contractAddress,
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

        txDAO.create(tnxHash, contract_address, 'shakeTestDrive', -1, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { _options })), on_chain_task_id)
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
          txDAO.create(-1, contract_address, 'shakeTestDrive', 0, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at submitShakeTestDriveTransaction');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
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
const submitCollectTestDriveTransaction = (_hid, _winner, _offchain, _nonce, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  console.log('submitCollectTestDriveTransaction');
  console.log(_hid, _winner, _offchain, contract_address, contract_json);
  return new Promise(async(resolve, reject) => {
    try {
      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const nonce           = _nonce;
      const gasPriceWei     = web3.utils.toWei(gasPrice, 'gwei');
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
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

        txDAO.create(tnxHash, contract_address, 'collectTestDrive', -1, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { _options })), on_chain_task_id)
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
          txDAO.create(-1, contract_address, 'collectTestDrive', 0, network_id, _offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at submitCollectTestDriveTransaction');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
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
 * @param {uint} fee
 * @param {bytes32} source
 * @param {uint} closingWindow
 * @param {uint} reportWindow
 * @param {uint} disputeWindow
 * @param {bytes32} offchain
 */

const createMarketTransaction = (_nonce, fee, source, closingTime, reportTime, dispute, offchain, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  return new Promise(async(resolve, reject) => {
    try {
      console.log('createMarketTransaction');
      console.log(_nonce, fee, source, closingTime, reportTime, dispute, offchain, contract_address, contract_json);
      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toWei(gasPrice, 'gwei');
      const nonce           = _nonce;
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
          from: ownerAddress
      });

      const rawTransaction = {
          'from'    : ownerAddress,
          'nonce'   : '0x' + nonce.toString(16),
          'gasPrice': web3.utils.toHex(gasPriceWei),
          'gasLimit': web3.utils.toHex(gasLimit),
          'to'      : contractAddress,
          'value'   : '0x0',
          'data'    : contract.methods.createMarket(fee, web3.utils.fromUtf8(source || '-'), closingTime, reportTime, dispute, web3.utils.fromUtf8(offchain)).encodeABI()
      };

      const tx                    = new ethTx(rawTransaction);
      tx.sign(privKey);
      const serializedTx          = tx.serialize();
      let tnxHash = -1;

      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, contract_address, 'createMarket', -1, network_id, offchain, JSON.stringify(Object.assign(rawTransaction, { _options })), on_chain_task_id)
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
          txDAO.create(-1, contract_address, 'createMarket', 0, network_id, offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at createMarketTransaction');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
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


/**
 * @param {address} creator
 * @param {uint} fee
 * @param {bytes32} source
 * @param {bool} isGrantedPermission
 * @param {uint} closingWindow
 * @param {uint} reportWindow
 * @param {uint} disputeWindow
 * @param {bytes32} offchain
 */

const createMarketForShurikenUserTransaction = (_nonce, creator, fee, source, isGrantedPermission, closingTime, reportTime, disputeTime, offchain, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  return new Promise(async(resolve, reject) => {
    try {
      console.log('createMarketForShurikenUserTransaction');
      console.log(_nonce, creator, fee, source, isGrantedPermission, closingTime, reportTime, disputeTime, offchain, contract_address, contract_json);
      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toWei(gasPrice, 'gwei');
      const nonce           = _nonce;
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
          from: ownerAddress
      });

      const rawTransaction = {
          'from'    : ownerAddress,
          'nonce'   : '0x' + nonce.toString(16),
          'gasPrice': web3.utils.toHex(gasPriceWei),
          'gasLimit': web3.utils.toHex(gasLimit),
          'to'      : contractAddress,
          'value'   : '0x0',
          'data'    : contract.methods.createMarketForShurikenUser(creator, fee, web3.utils.fromUtf8(source || '-'), isGrantedPermission, closingTime, reportTime, disputeTime, web3.utils.fromUtf8(offchain)).encodeABI()
      };

      const tx                    = new ethTx(rawTransaction);
      tx.sign(privKey);
      const serializedTx          = tx.serialize();
      let tnxHash = -1;

      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, contract_address, 'createMarketForShurikenUser', -1, network_id, offchain, JSON.stringify(Object.assign(rawTransaction, { _options })), on_chain_task_id)
        .catch(console.error);

        return resolve({
          raw: rawTransaction,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
        console.log('createMarketForShurikenUserTransactionReceipt');
        console.log(receipt);
      })
      .on('error', err => {
        console.log('createMarketForShurikenUserTransaction Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, contract_address, 'createMarketForShurikenUser', 0, network_id, offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at createMarketForShurikenUserTransaction');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
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


const reportOutcomeTransaction = (hid, outcome_id, outcome_result, nonce, _offchain, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  return new Promise(async(resolve, reject) => {
    try {
      const offchain = _offchain || ('cryptosign_report' + outcome_id + '_' + outcome_result);
      console.log('reportOutcomeTransaction');
      console.log(hid, outcome_result, nonce, _offchain, gasPrice, contract_address, contract_json);

      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toHex(web3.utils.toWei(gasPrice, 'gwei'));
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
          from: ownerAddress
      });

      const txParams = {
        gasPrice: gasPriceWei,
        gasLimit: web3.utils.toHex(gasLimit),
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

        txDAO.create(tnxHash, contract_address, 'report', -1, network_id, _offchain, JSON.stringify(Object.assign(txParams, { _options })), on_chain_task_id)
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
          txDAO.create(-1, contract_address, 'report', 0, network_id, _offchain, JSON.stringify(Object.assign(txParams, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at reportOutcomeTransaction');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
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


const reportOutcomeForCreatorTransaction = (hid, outcome_id, outcome_result, nonce, _offchain, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  return new Promise(async(resolve, reject) => {
    try {
      const offchain = _offchain || ('cryptosign_report' + outcome_id + '_' + outcome_result);
      console.log('reportOutcomeForCreatorTransaction');
      console.log(hid, outcome_result, nonce, _offchain, gasPrice, contract_address, contract_json);

      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toHex(web3.utils.toWei(gasPrice, 'gwei'));
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
          from: ownerAddress
      });

      const txParams = {
        gasPrice: gasPriceWei,
        gasLimit: web3.utils.toHex(gasLimit),
        to: contractAddress,
        from: ownerAddress,
        nonce: '0x' + nonce.toString(16),
        chainId: network_id,
        data: contract.methods.reportForCreator(hid, outcome_result, web3.utils.fromUtf8(offchain)).encodeABI()
      };

      const tx = new ethTx(txParams);
      let tnxHash = -1;
      tx.sign(privKey);

      const serializedTx = tx.serialize();

      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, contract_address, 'report', -1, network_id, _offchain, JSON.stringify(Object.assign(txParams, { _options })), on_chain_task_id)
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
          txDAO.create(-1, contract_address, 'report', 0, network_id, _offchain, JSON.stringify(Object.assign(txParams, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at reportOutcomeTransaction');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
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

const resolveOutcomeTransaction = (hid, outcome_result, nonce, _offchain, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  return new Promise(async(resolve, reject) => {
    try {
      const offchain = _offchain || ('cryptosign_resolve' + outcome_result);
      console.log('resolveOutcomeTransaction');
      console.log(hid, outcome_result, nonce, _offchain, gasPrice, contract_address, contract_json);

      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toHex(web3.utils.toWei(gasPrice, 'gwei'));
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
          from: ownerAddress
      });

      const txParams = {
        gasPrice: gasPriceWei,
        gasLimit: web3.utils.toHex(gasLimit),
        to: contractAddress,
        from: ownerAddress,
        nonce: '0x' + nonce.toString(16),
        chainId: network_id,
        data: contract.methods.resolve(hid, outcome_result, web3.utils.fromUtf8(offchain)).encodeABI()
      };

      const tx = new ethTx(txParams);
      let tnxHash = -1;
      tx.sign(privKey);

      const serializedTx = tx.serialize();

      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, contract_address, 'resolve', -1, network_id, _offchain, JSON.stringify(Object.assign(txParams, { _options })), on_chain_task_id)
        .catch(console.error);

        return resolve({
          raw: txParams,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
        console.log('resolve tnxHash: ', receipt);
      })
      .on('error', err => {
        console.log('resolveOutcomeTransaction Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, contract_address, 'resolve', 0, network_id, _offchain, JSON.stringify(Object.assign(txParams, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at resolveOutcomeTransaction');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
        }
        return reject({
          err_type: constants.TASK_STATUS.RESOLVE_TNX_FAIL,
          error: err,
          options_data: {
            task: _options.task
          }
        });
      });
    } catch (e) {
      reject({
        err_type: constants.TASK_STATUS.RESOLVE_TNX_EXCEPTION,
        error: e,
        options_data: {
          task: _options.task
        }
      });
    }
  });
};

const uninitForTrial = (_hid, _side, _odds, _maker, _value, _offchain, _nonce, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  return new Promise(async(resolve, reject) => {
    try {
      console.log('uninitForTrial');
      console.log(_hid, _side, _odds, _maker, _value, _nonce, _offchain, _options, contract_address, contract_json);

      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toHex(web3.utils.toWei(gasPrice, 'gwei'));
      const value           = web3.utils.toHex(web3.utils.toWei(_value));
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
          from: ownerAddress
      });

      const txParams = {
        gasPrice: gasPriceWei,
        gasLimit: web3.utils.toHex(gasLimit),
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

        txDAO.create(tnxHash, contract_address, 'uninitForTrial', -1, network_id, _offchain, JSON.stringify(Object.assign(txParams, { _options })), on_chain_task_id)
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
          txDAO.create(-1, contract_address, 'uninitForTrial', 0, network_id, _offchain, JSON.stringify(Object.assign(txParams, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at uninitForTrial');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
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


const uninitMaster = (_hid, _side, _odds, _stake, _offchain, _nonce, gasPrice, _options, contract_address, contract_json, on_chain_task_id) => {
  return new Promise(async(resolve, reject) => {
    try {
      console.log('uninitMaster');
      console.log(_hid, _side, _odds, _stake, _nonce, _offchain, _options, contract_address, contract_json);

      const contractAddress = contract_address;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toHex(web3.utils.toWei(gasPrice, 'gwei'));
      const stake           = web3.utils.toHex(web3.utils.toWei(_stake));
      const contract        = new web3.eth.Contract(loadABI(contract_json), contractAddress, {
          from: ownerAddress
      });

      const txParams = {
        gasPrice: gasPriceWei,
        gasLimit: web3.utils.toHex(gasLimit),
        to: contractAddress,
        from: ownerAddress,
        nonce: '0x' + _nonce.toString(16),
        chainId: network_id,
        data: contract.methods.uninit(_hid, _side, _odds, stake, web3.utils.fromUtf8(_offchain)).encodeABI()
      };

      const tx = new ethTx(txParams);
      let tnxHash = -1;
      tx.sign(privKey);

      const serializedTx = tx.serialize();

      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, contract_address, 'uninitMaster', -1, network_id, _offchain, JSON.stringify(Object.assign(txParams, { _options })), on_chain_task_id)
        .catch(console.error);

        return resolve({
          raw: txParams,
          hash: hash,
          task: _options.task
        });
      })
      .on('receipt', (receipt) => {
        console.log('uninitMaster tnxHash: ', receipt);
      })
      .on('error', err => {
        console.log('uninitMaster Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, contract_address, 'uninitMaster', 0, network_id, _offchain, JSON.stringify(Object.assign(txParams, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at uninitMaster');
            web3Config.setNonce(web3Config.getNonce() -1);
          }
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
  reportOutcomeForCreatorTransaction,
  resolveOutcomeTransaction,
  submitShakeTransaction,
  submitShakeTestDriveTransaction,
  submitCollectTestDriveTransaction,
  uninitForTrial,
  uninitMaster,
  createMarketForShurikenUserTransaction
};
