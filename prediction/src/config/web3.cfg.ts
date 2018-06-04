
const Web3 = require('web3');
const net = require('net');

// import * as net from 'net';

let web3: any;
/**
 * create node server connection
 */
export let connectWeb3Server = (options: any) => {
  if (options.http) {
    web3 = new Web3(new Web3.providers.HttpProvider(options.http));
  }
  else if (options.ipc) {
    web3 = new Web3(options.ipc, net);
  }
  else if (options.ws) {
    web3 = new Web3(Web3.givenProvider || options.ws);
  }
};

export let Web3Provider = (): any => {
  return web3;
};
