
const Web3 = require('web3');
const configs = require('../configs');
const PredictionHandshake = require('../contracts/PredictionHandshake.json');
var web3 = new Web3(new Web3.providers.HttpProvider(configs.network[4].blockchainNetwork));
var contractPredictionAddress = configs.network[4].predictionHandshakeAddress;
var ownerAddress = configs.network[4].ownerAddress;
var privateKey = configs.network[4].privateKey;
var gasLimit = configs.network[4].gasLimit;

var contractPredictionHandshake = new web3.eth.Contract(PredictionHandshake.abi, contractPredictionAddress);

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

const getNonce = (address, status) => {
  status = status ? status : 'latest';
  return web3.eth.getTransactionCount(address, status);
};

const getGasPrice = async () => {
  return await web3.eth.getGasPrice();
};

// /*
//     submit init transaction
// */
const submitInitTransaction = (_hid, _side, _payout, _offchain) => {
  return new Promise(async(resolve, reject) => {
    const contractAddress = contractPredictionAddress;
    const privKey         = Buffer.from(privateKey, 'hex');
    const gasPriceWei     = await getGasPrice();
    const nonce           = await getNonce(ownerAddress);
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
        'data'    : contract.methods.init(_hid, _side, _payout, web3.utils.fromUtf8(_offchain)).encodeABI()
    };

    const tx                    = new ethTx(rawTransaction);
    tx.sign(privKey);
    const serializedTx          = tx.serialize();
    let transactionHash    = '-';

    web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
    .on('transactionHash', (hash) => {
        transactionHash = hash;
        console.log('transactionHash: ', transactionHash);
    })
    .on('receipt', (receipt) => {
      return resolve(receipt);
    })
    .catch((err) => {
        const error = err.toString();
        let _err = {};
        if (error.indexOf('Transaction was not mined within 50 blocks') > 0) {
            _err = {
                status: '0x2',
                error : err.toString(),
                data  : rawTransaction,
                transactionHash  : transactionHash
            };
        }
        else if (error.indexOf('known transaction') > 0) {
          _err = {
                status: '0x3',
                error : err.toString(),
                data  : rawTransaction,
                transactionHash  : transactionHash
            };
        }
        else if (error.indexOf('Failed to check for transaction receipt') > 0) {
          _err = {
                status: '0x4',
                error : err.toString(),
                data  : rawTransaction,
                transactionHash  : transactionHash
            };
        }
        else {
          _err = {
            status: '0x0',
            error : err.toString(),
            data  : rawTransaction,
            transactionHash  : transactionHash
          };
        }
        return reject(_err);
    });
  });
};

const submitMultiInitTransaction = (_hids, _sides, _payouts, _offchains) => {
  return new Promise(async(resolve, reject) => {
    const contractAddress = contractPredictionAddress;
    const privKey         = Buffer.from(privateKey, 'hex');
    const gasPriceWei     = await getGasPrice();
    const nonce           = await getNonce(ownerAddress);
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
        'data'    : contract.methods.multiInit(_hids, _sides, _payouts, _offchains).encodeABI()
    };

    const tx                    = new ethTx(rawTransaction);
    tx.sign(privKey);
    const serializedTx          = tx.serialize();
    let transactionHash    = '-';

    web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
    .on('transactionHash', (hash) => {
        transactionHash = hash;
        console.log('transactionHash: ', transactionHash);
    })
    .on('receipt', (receipt) => {
      return resolve(receipt);
    })
    .catch((err) => {
        const error = err.toString();
        let _err = {};
        if (error.indexOf('Transaction was not mined within 50 blocks') > 0) {
            _err = {
                status: '0x2',
                error : err.toString(),
                data  : rawTransaction,
                transactionHash  : transactionHash
            };
        }
        else if (error.indexOf('known transaction') > 0) {
          _err = {
                status: '0x3',
                error : err.toString(),
                data  : rawTransaction,
                transactionHash  : transactionHash
            };
        }
        else if (error.indexOf('Failed to check for transaction receipt') > 0) {
          _err = {
                status: '0x4',
                error : err.toString(),
                data  : rawTransaction,
                transactionHash  : transactionHash
            };
        }
        else {
          _err = {
            status: '0x0',
            error : err.toString(),
            data  : rawTransaction,
            transactionHash  : transactionHash
          };
        }
        return reject(_err);
    });
  });
};

module.exports = { submitInitTransaction, submitMultiInitTransaction };
