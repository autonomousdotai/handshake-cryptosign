# -*- coding: utf-8 -*-
STATUS = {
	'STATUS_UNACTIVE': 0,
	'STATUS_ACTIVE': 1
}

# user
User = STATUS.copy()
User['STATUS_LOCKED'] = 2
User['STATUS_OPTIONS'] = {
	User['STATUS_UNACTIVE']: 'Unactive',
	User['STATUS_ACTIVE']: 'Active',
	User['STATUS_LOCKED']: 'Locked'
}

# wallet
Wallet = STATUS.copy()
Wallet['STATUS_OPTIONS'] = {
	Wallet['STATUS_UNACTIVE']: 'Unactive',
	Wallet['STATUS_ACTIVE']: 'Active',
}

# subscription type

Subscription = {
	'TRIAL': 5,
	'TIER_5': 5,
	'TIER_15': 20,
	'TIER_30': 50,
}

# handshake
Handshake = {
	'STATUS_BLOCKCHAIN_PENDING': -4,
	'STATUS_NEW': -3,
	'STATUS_TRANSACTION_FAILED': -2,
	'STATUS_PENDING': -1,
	'STATUS_INITED': 0,
	'STATUS_SHAKED': 1,
	'STATUS_ACCEPTED': 2,
	'STATUS_REJECTED': 3,
	'STATUS_DONE': 4,
	'STATUS_CANCELLED': 5,

	'STATUS_GROUP_INITED': 0,
	'STATUS_GROUP_SHAKED': 1,
	'STATUS_GROUP_DONE': 2,

	'TERM_NONE': 0,
	'TERM_COD': 1,
	'TERM_NET30': 2,
	'TERM_VESTING': 3,

	'INDUSTRIES_NONE': 0,
	'INDUSTRIES_UPLOAD_DOCUMENT': 13,
	'INDUSTRIES_BETTING': 3
}

Handshake['STATUS_OPTIONS'] = {
	Handshake['STATUS_PENDING']: 'Pending',
	Handshake['STATUS_INITED']: 'Inited',
	Handshake['STATUS_SHAKED']: 'Shaked',
	Handshake['STATUS_ACCEPTED']: 'Accepted',
	Handshake['STATUS_REJECTED']: 'Rejected',
	Handshake['STATUS_DONE']: 'Done',
	Handshake['STATUS_CANCELLED']: 'Cancelled',
}

Handshake['TERM_OPTIONS'] = {
	Handshake['TERM_NONE']: 'None',
	Handshake['TERM_COD']: 'COD',
	Handshake['TERM_NET30']: 'Net 30',
	Handshake['TERM_VESTING']: 'Vesting',
}

Tx = {
	'STATUS_PENDING': -1,
	'STATUS_FAILED': 0,
	'STATUS_SUCCESS': 1,
}

Tx['STATUS_OPTIONS'] = {
	Tx['STATUS_PENDING']: 'Pending',
	Tx['STATUS_FAILED']: 'Failed',
	Tx['STATUS_SUCCESS']: 'Success',
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
	'SHAKE': 2,
	'SHAKED': 3,
	'DELIVER': 4,
	'REJECT': 5,
	'DONE': 6
}

CRYPTOSIGN_OFFCHAIN_PREFIX = 'cryptosign_'

# COMMUNITY_TYPE
COMMUNITY_TYPE = {
	'PUBLIC': 0,
	'PRIVATE': 1
}

STATE_TYPE = {
	'NEW': 0,
	'PUBLISH': 1
}