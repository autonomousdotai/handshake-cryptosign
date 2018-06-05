
import * as fs from 'fs';

let localConfig = {};
let envConfig = {};

if (fs.existsSync(__dirname + '/config-local.js')) {
  localConfig = require('./config-local');
}

const baseConfig = {
  db: {
    database: 'cryptosign',
    username: 'root',
    password: 'root',
    host: 'localhost',
    dialect: 'mysql',
    pool: {
      max: 5,
      min: 0,
      idle: 10000
    }
  },
  port: 5000,
  timeAlive: 60,
  restApiEndpoint: process.env.CRYPTOSIGN_RESTAPI_ENDPOINT || 'http://localhost:5000',
  network: {
    '1': {
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '',
      blockchainNetwork: 'https://mainnet.infura.io/',
    },
    '4': {
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '',
      blockchainNetwork: 'https://rinkeby.infura.io/',
    },
    '5': {
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '',
      blockchainNetwork: 'http://localhost:8545',
    }
  }
};

const envs = {
  'staging': 'config-staging',
  'production': 'config-production',
} as any;

const env = process.env.NODE_ENV || 'default';

if (envs[env] !== undefined ) {
  if (fs.existsSync(__dirname + '/' + envs[env] + '.ts')) {
    envConfig = require('./' + envs[env]);
  }
}

module.exports = Object.assign({}, baseConfig, envConfig, localConfig);
