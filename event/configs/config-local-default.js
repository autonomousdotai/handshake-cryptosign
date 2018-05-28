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
      basicHandshakeAddress: '0xefe5de6b5832fa25960b421dffc3b501815b280e',
      payableHandshakeAddress: '0x163a948770020a636a87a48acb33d7575445474b',
      blockchainNetwork: 'https://mainnet.infura.io/',
    },
    '4': {
      basicHandshakeAddress: '0x4c621cfd5496b2077eb1c5b0308e2ea72358191b',
      payableHandshakeAddress: '0x7e887002a227488fafb6db94a11abf281b62b4da',
      blockchainNetwork: 'https://rinkeby.infura.io/',
    },
    '5': { 
      basicHandshakeAddress: '0x8b7c973194de5cfbdd4b3335c719907a721d4ee5',
      payableHandshakeAddress: '0x1173df104e6c8bea66d8c199853d0e89dcae6b98',
      blockchainNetwork: 'http://localhost:8545',
    }
  }
}
