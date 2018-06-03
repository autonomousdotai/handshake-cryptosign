module.exports = {
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
}
