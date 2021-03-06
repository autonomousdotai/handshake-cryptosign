# -*- coding: utf-8 -*-
from decimal import *


Tx = {
	'STATUS_PENDING': -1,
	'STATUS_DONE': 0
}

# handshake
Handshake = {
	'STATUS_MAKER_SHOULD_UNINIT': -12,

	'STATUS_SHAKE_FAILED': -11,
	'STATUS_INIT_FAILED': -10,

	'STATUS_COLLECT_FAILED': -9,
	'STATUS_COLLECT_PENDING': -8,

	'STATUS_DISPUTE_FAILED': -7,
	'STATUS_REFUND_FAILED': -6,
	'STATUS_REFUND_PENDING': -13,
	'STATUS_DISPUTE_PENDING': -14,

	'STATUS_MAKER_UNINIT_FAILED': -5,
	'STATUS_MAKER_UNINIT_PENDING': -4,

	'STATUS_SHAKER_ROLLBACK': -3,
	'STATUS_MAKER_INIT_ROLLBACK': -2,
	'STATUS_PENDING': -1,
	
	'STATUS_INITED': 0,
	'STATUS_MAKER_UNINITED': 1,
	'STATUS_SHAKER_SHAKED': 2,
	'STATUS_REFUNDED': 3,
	'STATUS_USER_DISPUTED': 7,
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

CRYPTOSIGN_OFFCHAIN_PREFIX = 'cryptosign_'
CRYPTOSIGN_ERC20_OFFCHAIN_PREFIX = 'cryptosignERC20_'
CRYPTOSIGN_MINIMUM_MONEY = '0.0005'
CRYPTOSIGN_MAXIMUM_MONEY = '0.5'
CRYPTOSIGN_FREE_BET_AMOUNT = '0.03'

SOURCE_URL_ICON = 'https://api.faviconkit.com/{}/32'
SOURCE_GC_DOMAIN = 'https://storage.googleapis.com/{}/{}/{}'

UPLOAD_ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
CROP_ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']
UPLOAD_MAX_FILE_SIZE = 2 * 1024 * 1024
IMAGE_CROP_WIDTH = 640
IMAGE_CROP_HEIGHT =  IMAGE_CROP_WIDTH * 9 / 16
IMAGE_NAME_SOURCE_DEFAULT = 'source_default.jpg'

COMMUNITY_TYPE = {
	'PUBLIC': 0,
	'PRIVATE': 1
}

CONTRACT_TYPE = {
	'ETH': 'ETH',
	'ERC20': 'ERC20'
}

STATE_TYPE = {
	'NEW': 0,
	'PUBLISH': 1
}

RESULT_TYPE = {
	'REPORT_FAILED': -5,
	'DISPUTED': -3,
	'PROCESSING': -2,
	'PENDING': -1,
	'SUPPORT_WIN': 1,
	'AGAINST_WIN': 2,
	'DRAW': 3
}

SIDE_TYPE = {
	'SUPPORT': 1,
	'OPPOSE': 2
}

SHURIKEN_TYPE = {
	'FREE': '0',
	'REAL': '1'
}

TASK_TYPE = {
	'FREE_BET': 'FREE_BET',
	'REAL_BET': 'REAL_BET',
	'NORMAL': 'NORMAL',
	'ERC_20': 'ERC_20'
}

TASK_ACTION = {
	'INIT': 'INIT',
	'UNINIT': 'UNINIT',
	'COLLECT': 'COLLECT',
	'REPORT': 'REPORT',
	'RESOLVE': 'RESOLVE',
	'CREATE_MARKET': 'CREATE_MARKET',
	'ADD_FEED': 'ADD_FEED',
	'ADD_TOKEN': 'ADD_TOKEN',
	'APPROVE_TOKEN': 'APPROVE_TOKEN'
}

TOKEN_STATUS = {
	'PENDING': -1,
	'REJECTED': 0,
	'APPROVED': 1
}

SETTING_TYPE = {
	'TASK_CRON_JOB': 'TaskCronJob',
	'GAS_PRICE': 'GasPrice',
	'ONCHAIN_CRON_JOB': 'OnchainCronJob',
	'FREE_BET': 'FreeBet',
	'BOT': 'Bot'
}

OUTCOME_STATUS = {
	'REJECTED': -1,
	'PENDING': 0,
	'APPROVED': 1
}

OUTCOME_DEFAULT_NAME = "Yes"
