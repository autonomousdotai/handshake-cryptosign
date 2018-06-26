module.exports = {
  TASK_STATUS: {
    'STATUS_FAILED': 0,
    'STATUS_SUCCESS': 1,
    'STATUS_PENDING': -1,
    'STATUS_RETRY': -2,
    'STATUS_PROGRESSING': -3,
    'STATUS_CALL_SMARTCONTRACT_FAIL': -4
  },
  TASK_TYPE: {
    'FREE_BET': 'FREE_BET',
    'REAL_BET': 'REAL_BET'
  },
  TASK_ACTION: {
    'INIT': 'INIT',
    'UNINIT': 'UNINIT',
    'COLLECT': 'COLLECT',
    'CREATE_MARKET': 'CREATE_MARKET'
  }
}