
import { Web3Provider } from 'web3.cfg';
import { BigNumber } from 'bignumber.js';
// import * as moment from 'moment';
// const ethTx = require('ethereumjs-tx');

/* PRIVATE FUNCTIONS */

/* PUBLIC FUNCTIONS */
export const padLeftEven = (hex: string): string => {
  hex = hex.length % 2 !== 0 ? '0' + hex : hex;
  return hex;
};

export const padLeft = (n: any, width: number, z?: string) => {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
};

export const padRight = (n: any, width: number, z?: string) => {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : n + new Array(width - n.length + 1).join(z);
};

export const stringToHex = (tmp: string) => {
  let str = '';
  for (let i = 0; i < tmp.length; i++) {
    str += tmp[i].charCodeAt(0).toString(16);
  }
  return str;
};

export const decimalToHex = (dec: BigNumber.Value) => {
  return new BigNumber(dec).toString(16);
};

export const getNaked = (address: string): string => {
  return address.toLowerCase().replace('0x', '');
};

export const isAddress = (address: string) => {
  const web3 =  Web3Provider();
  if (!/^(0x|0X)?[a-fA-F0-9]+$/.test(address)) {
    return false;
  }
  return web3.utils.isAddress(address);
};

export const IsNumberUppercaseString = (string: string) => {
  return (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/).test(string);
};

export const getBalance = (obj: any): Promise<object> => {
  const web3 =  Web3Provider();
  return web3.eth.getBalance(obj.address).then((result: string) => {
    obj.balance = result; // web3.utils.hexToNumber(web3.utils.numberToHex(result));
    return obj;
  });
};

export const sanitizeHex = (hex: string) => {
  hex = hex.substring(0, 2) === '0x' ? hex.substring(2) : hex;
  if (hex === '') {
    return '';
  }
  return '0x' + padLeftEven(hex);
};

export let getNonce = (address: string, status?: string) => {
  const web3 =  Web3Provider();
  try {
    status = status ? status : 'latest';
    return web3.eth.getTransactionCount(address, status);
  } catch (er) {
    return null;
  }
};

export let getGasPrice = (isMin?: boolean): Promise<string> => {
  return new Promise<string>((resolve, reject) => {
    const web3 =  Web3Provider();
    web3.eth.getGasPrice().then((gasPrice: string) => {
      return resolve(gasPrice);
    })
  .catch(reject);
  });
};

export let getTransactionReceipt = (tnxHash: string): Promise<any> => {
  return new Promise<any>((resolve, reject) => {
    const web3 =  Web3Provider();
    web3.eth.getTransaction(tnxHash)
    .then((tnx: any) => {
      web3.eth.getTransactionReceipt(tnxHash)
      .then((tnxReceipt: any) => {
        tnxReceipt.nonce = tnx.nonce;
        return resolve(tnxReceipt);
      })
      .catch(reject);
    })
    .catch(reject);
  });
};

// /*
//     submit transaction
// */

// export const submitTransaction = async(data: any) => {
//     const web3 =  Web3Provider();
//     if (amountDecimal <= 0
//         || destAddress === process.env.OWNER_ADDRESS
//         || destAddress === '0x00') return false;
//     const y: any          = process.env.DECIMALS;
//     const contractAddress = process.env.CONTRACT_ADDRESSS;
//     const ownerAddress    = process.env.OWNER_ADDRESS;
//     const priKey          = process.env.PRI_KEY;
//     const privKey         = new Buffer(priKey, 'hex');
//     const transferAmount  = (new BigNumber(`${amountDecimal}`)).times(10 ** y);
//     const gasPriceWei     = await getGasPrice(true);
//     const nonce           = await getNonce(ownerAddress);
//     const contract        = new web3.eth.Contract(NoahABI, contractAddress, {
//         from: ownerAddress
//     });
//     const balance         = await contract.methods.balanceOf(ownerAddress).call();
//     if (transferAmount.isGreaterThan(balance)) return false;
//     const rawTransaction = {
//         'from'    : ownerAddress,
//         'nonce'   : '0x' + nonce.toString(16),
//         'gasPrice': web3.utils.toHex(gasPriceWei),
//         'gasLimit': web3.utils.toHex(parseInt(process.env.GAS_LIMIT)),
//         'to'      : contractAddress,
//         'value'   : '0x0',
//         'data'    : contract.methods.transfer(destAddress, sanitizeHex(transferAmount.toString(16))).encodeABI()
//     };

//     const tx                    = new ethTx(rawTransaction);
//     tx.sign(privKey);
//     const serializedTx          = tx.serialize();
//     let transactionHash: any    = +moment.utc();
//     return web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'))
//     .on('transactionHash', (hash: string) => {
//         transactionHash = hash;
//     })
//     .on('receipt', (receipt: any) => {
//       return receipt;
//     })
//     .catch((err: any) => {
//         const error = err.toString();
//         if (error.indexOf('Transaction was not mined within 50 blocks') > 0)
//             return {
//                 status: '0x2',
//                 error : err.toString(),
//                 data  : rawTransaction,
//                 transactionHash  : transactionHash
//             };
//         else if (error.indexOf('known transaction') > 0)
//             return {
//                 status: '0x3',
//                 error : err.toString(),
//                 data  : rawTransaction,
//                 transactionHash  : transactionHash
//             };
//         else if (error.indexOf('Failed to check for transaction receipt') > 0)
//             return {
//                 status: '0x4',
//                 error : err.toString(),
//                 data  : rawTransaction,
//                 transactionHash  : transactionHash
//             };
//         return {
//             status: '0x0',
//             error : err.toString(),
//             data  : rawTransaction,
//             transactionHash  : transactionHash
//         };
//     });
// };
