# -*- coding: utf-8 -*-
from decimal import *


Tx = {
	'STATUS_PENDING': -1,
	'STATUS_DONE': 0
}

# handshake
Handshake = {
	'STATUS_SHAKE_FAILED': -11,
	'STATUS_INIT_FAILED': -10,

	'STATUS_COLLECT_FAILED': -9,
	'STATUS_COLLECT_PENDING': -8,

	'STATUS_DISPUTE_FAILED': -7,
	'STATUS_REFUND_FAILED': -6,

	'STATUS_MAKER_UNINIT_FAILED': -5,
	'STATUS_MAKER_UNINIT_PENDING': -4,

	'STATUS_SHAKER_ROLLBACK': -3,
	'STATUS_MAKER_INIT_ROLLBACK': -2,
	'STATUS_PENDING': -1,
	
	'STATUS_INITED': 0,
	'STATUS_MAKER_UNINITED': 1,
	'STATUS_SHAKER_SHAKED': 2,
	'STATUS_REFUNDED': 3,
	'STATUS_DISPUTED': 4,
	'STATUS_RESOLVED': 5,
	'STATUS_DONE': 6,

	'INDUSTRIES_NONE': 0,
	'INDUSTRIES_UPLOAD_DOCUMENT': 13,
	'INDUSTRIES_BETTING': 3
}


BLOCKCHAIN_NETWORK = {
	'MAIN': 1,
	'ROPSTEN': 2,
	'KOVAN': 3,
	'RINKEBY': 4,
	'LOCAL': 5
}

# Handshake state
HANDSHAKE_STATE = {
	'INIT': 0,
	'INTIATED': 1,
	'UNINIT': 2,
	'UNINITED': 3,
	'SHAKE': 4,
	'SHAKED': 5,
	'COLLECT': 6,
	'REFUND': 7,
	'DONE': 8
}

CRYPTOSIGN_OFFCHAIN_PREFIX = 'cryptosign_'
CRYPTOSIGN_MINIMUM_MONEY = Decimal('0.0005')

# COMMUNITY_TYPE
COMMUNITY_TYPE = {
	'PUBLIC': 0,
	'PRIVATE': 1
}

STATE_TYPE = {
	'NEW': 0,
	'PUBLISH': 1
}

RESULT_TYPE = {
	'PENDING': -1,
	'DRAW': 0,
	'SUPPORT_WIN': 1,
	'AGAINST_WIN': 2
}

SIDE_TYPE = {
	'DRAW': 0,
	'SUPPORT': 1,
	'AGAINST': 2
}

SHURIKEN_TYPE = {
	'FREE': '0',
	'REAL': '1'
}

TASK_TYPE = {
	'FREE_BET': 'FREE_BET',
	'REAL_BET': 'REAL_BET'
}

TASK_ACTION = {
	'INIT': 'INIT',
	'UNINIT': 'UNINIT',
	'COLLECT': 'COLLECT',
	'REPORT': 'REPORT',
	'CREATE_MARKET': 'CREATE_MARKET'
}