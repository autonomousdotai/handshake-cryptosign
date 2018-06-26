module.exports = {
  TASK_STATUS: {
    'STATUS_PROGRESSING': -3,
    'STATUS_RETRY': -2,
    'STATUS_PENDING': -1,
    'STATUS_FAILED': 0,
    'STATUS_SUCCESS': 1,
  },
  TASK_TYPE = {
    'FREE_BET': 'FREE_BET',
    'REAL_BET': 'REAL_BET'
  },
  TASK_ACTION = {
    'INIT': 'INIT',
    'UNINIT': 'UNINIT',
    'COLLECT': 'COLLECT',
    'CREATE_MARKET': 'CREATE_MARKET'
  }
}