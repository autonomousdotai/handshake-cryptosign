
const configs = require('../configs');
const constants = require('../constants');

// models
const txDAO = require('../daos/tx');
const web3 = require('../configs/web3').getWeb3();
const web3Config = require('../configs/web3');

const network_id = configs.network_id;
const tokenRegistryAddress = configs.network[network_id].tokenRegistryAddress;
const ownerAddress = configs.network[network_id].ownerAddress;
const privateKey = configs.network[network_id].privateKey;
const gasLimit = configs.network[network_id].gasLimit;

const ethTx = require('ethereumjs-tx');
const tokenRegistryAbi = require('../contracts/TokenRegistry.json').abi;

/**
 * @param {address} _tokenAddr
 * @param {string} _symbol
 * @param {string} _name
 * @param {string} _decimals
 * @param {bytes32} offchain
 */

const addNewTokenTransaction = (_nonce, _tokenAddr, _symbol, _name, _decimals, offchain, gasPrice, _options, on_chain_task_id) => {
  return new Promise(async(resolve, reject) => {
    try {
      const contractAddress = tokenRegistryAddress;
      const privKey         = Buffer.from(privateKey, 'hex');
      const gasPriceWei     = web3.utils.toWei(gasPrice, 'gwei');
      const nonce           = _nonce;
      const contract        = new web3.eth.Contract(tokenRegistryAbi, contractAddress, {
          from: ownerAddress
      });

      const rawTransaction = {
          'from'    : ownerAddress,
          'nonce'   : '0x' + nonce.toString(16),
          'gasPrice': web3.utils.toHex(gasPriceWei),
          'gasLimit': web3.utils.toHex(gasLimit),
          'to'      : contractAddress,
          'value'   : '0x0',
          'data'    : contract.methods.addNewToken(_tokenAddr, _symbol, _name, _decimals, web3.utils.fromUtf8(offchain)).encodeABI()
      };

      const tx = new ethTx(rawTransaction);
      tx.sign(privKey);
      const serializedTx = tx.serialize();
      let tnxHash = -1;

      web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
      .on('transactionHash', (hash) => {
        tnxHash = hash;

        txDAO.create(tnxHash, tokenRegistryAddress, 'addNewToken', -1, network_id, offchain, JSON.stringify(Object.assign(rawTransaction, { _options })), on_chain_task_id)
        .catch(console.error);

        return resolve({
          raw: rawTransaction,
          hash: hash,
          task: _options.task
        });
      })
      .on('error', err => {
        console.log('addNewTokenTransaction Error');
        console.log(err);
        // Fail at offchain
        if (tnxHash == -1) {
          txDAO.create(-1, tokenRegistryAddress, 'addNewToken', 0, network_id, offchain, JSON.stringify(Object.assign(rawTransaction, { err: err.message, _options, tnxHash })), on_chain_task_id)
          .catch(console.error);
        } else {
          if (!(err.message || err).includes('not mined within 50 blocks')) {
            console.log('Remove nonce at addNewTokenTransaction');
            web3Config.setNonce(web3Config.getNonce() - 1);
          }
        }
        return reject({
          err_type: constants.TASK_STATUS.ADD_TOKEN_FAILED,
          error: err,
          options_data: {
            task: _options.task
          }
        });
      });
    } catch (e) {
      reject({
        err_type: constants.TASK_STATUS.ADD_TOKEN_TNX_EXCEPTION,
        error: e,
        options_data: {
          task: _options.task
        }
      });
    }
  });
};


module.exports = {
  addNewTokenTransaction
};
