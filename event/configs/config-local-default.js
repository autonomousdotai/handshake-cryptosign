module.exports = {
  db: {
    database: '',
    username: '',
    password: '',
    host: '',
    dialect: 'mysql',
    pool: {
      max: 5,
      min: 0,
      idle: 10000
    }
  },
  port: 5000,
  timeAlive: 60,
  restApiEndpoint: process.env.CRYPTOSIGN_RESTAPI_ENDPOINT || 'localhost',
  restApiEndpointPort: process.env.CRYPTOSIGN_RESTAPI_ENDPOINT_PORT || 5000,
  payload: process.env.CRYPTOSIGN_RESTAPI_PAYLOAD || '',
  network_id: 4,
  network: {
    '1': {
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '',
      ownerAddress: '',
      privateKey: '',
      gasLimit: 3000000,
      blockchainNetwork: 'https://mainnet.infura.io/',
    },
    '4': {
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '',
      ownerAddress: '',
      privateKey: '',
      gasLimit: 3000000,
      blockchainNetwork: 'https://rinkeby.infura.io/',
    },
    '5': { 
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '',
      ownerAddress: '',
      privateKey: '',
      gasLimit: 3000000,
      blockchainNetwork: 'http://localhost:8545',
    }
  }
}
