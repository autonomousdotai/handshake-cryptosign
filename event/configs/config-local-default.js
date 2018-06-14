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
  port: 3000,
  timeAlive: 60,
  restApiEndpoint: process.env.CRYPTOSIGN_RESTAPI_ENDPOINT || 'http://localhost:5000',
  payload: process.env.CRYPTOSIGN_RESTAPI_PAYLOAD || '',
  fcm_token: process.env.CRYPTOSIGN_RESTAPI_FCM_TOKEN || '',
  uid: process.env.CRYPTOSIGN_RESTAPI_UID || 1,
  network_id: 4,
  network: {
    '1': {
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '0x53d062575cef3df834d09f26784eff501b9550fa',
      ownerAddress: '',
      privateKey: '',
      gasLimit: 1000000,
      gasPrice: 4,
      amountValue: 0.001,
      blockchainNetwork: 'https://mainnet.infura.io/',
    },
    '4': {
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '',
      ownerAddress: '',
      privateKey: '',
      gasLimit: 3000000,
      gasPrice: 100,
      amountValue: 0.001,
      blockchainNetwork: 'https://rinkeby.infura.io/',
    },
    '5': { 
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '',
      ownerAddress: '',
      privateKey: '',
      gasLimit: 3000000,
      gasPrice: 2.1,
      amountValue: 0.001,
      blockchainNetwork: 'http://localhost:8545',
    }
  }
}
