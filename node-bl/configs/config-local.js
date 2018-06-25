module.exports = {
  db: {
    database: 'local_db',
    username: 'root',
    password: 'root',
    host: 'localhost',
    // database: 'staging_cryptosign',
    // username: 'root',
    // password: 'Jz3n55skvJzqooxz',
    // host: '35.203.184.211',
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
  payload: process.env.CRYPTOSIGN_RESTAPI_PAYLOAD || 'yR-jRm9facH9hIGSS0zXL1klK3V7Lo-QgN80gNcdXyxbV95o8-HsfnDHWg==',
  fcm_token: process.env.CRYPTOSIGN_RESTAPI_FCM_TOKEN || '',
  uid: process.env.CRYPTOSIGN_RESTAPI_UID || 1,
  network_id: 4,
  network: {
    '1': {
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '',
      ownerAddress: '',
      privateKey: '',
      gasLimit: 3000000,
      gasPrice: 100,
      amountValue: 0.001,
      blockchainNetwork: 'https://mainnet.infura.io/',
    },
    '4': {
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '0x6f25814d49bcf8345f8afd2a3bf9d5fd95079f84',
      ownerAddress: '0xeA5baf7008Cda0E970F91b01F52F4216696c8Fc3',
      privateKey: '6523041216c810af470944435adfc3910a4a69644209e1b196eb731300d71a8d',
      gasLimit: 3000000,
      gasPrice: 100,
      amountValue: 0.001,
      reportTimeConfig: 0.2,
      blockchainNetwork: 'https://rinkeby.infura.io/',
    },
    '5': { 
      basicHandshakeAddress: '',
      payableHandshakeAddress: '',
      bettingHandshakeAddress: '',
      ownerAddress: '',
      privateKey: '',
      gasLimit: 3000000,
      gasPrice: 100,
      amountValue: 0.001,
      blockchainNetwork: 'http://localhost:8545',
    }
  }
}
