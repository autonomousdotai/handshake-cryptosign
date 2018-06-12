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
  restApiEndpoint: process.env.CRYPTOSIGN_RESTAPI_ENDPOINT || 'http://localhost:5000',
  payload: process.env.CRYPTOSIGN_RESTAPI_PAYLOAD || '',
  fcm_token: process.env.CRYPTOSIGN_RESTAPI_FCM_TOKEN || '',
  uid: process.env.CRYPTOSIGN_RESTAPI_UID || 0,
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
