module.exports = {
  Tx: {
    'STATUS_PENDING': -1,
    'STATUS_FAILED': 0,
    'STATUS_SUCCESS': 1,
  },
  Handshake: {
    'STATUS_TRANSACTION_FAILED': -2,
    'STATUS_PENDING': -1,
    'STATUS_INITED': 0,
    'STATUS_SHAKED': 1,
    'STATUS_ACCEPTED': 2,
    'STATUS_REJECTED': 3,
    'STATUS_DONE': 4,
    'STATUS_CANCELLED': 5,
    'TERM_NONE': 0,
    'TERM_COD': 1,
    'TERM_NET30': 2,
    'TERM_VESTING': 3,
  },
  Wallet: {
    'STATUS_UNACTIVE': 0,
    'STATUS_ACTIVE': 1
  },
  User: {
    'STATUS_UNACTIVE': 0,
    'STATUS_ACTIVE': 1,
    'STATUS_LOCKED': 2,
  },

  CRYPTOSIGN_OFFCHAIN_PREFIX: 'cryptosign',
}