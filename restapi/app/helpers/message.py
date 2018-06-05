#!/usr/bin/python
# -*- coding: utf-8 -*-

class MESSAGE(object):
	# ERROR
	INVALID_DATA = 'Please double check your input data.'
	INVALID_BET = 'There is something wrong with your bet.'
	BET_NOT_FOUND = 'There is no bet which match your side. Please create a new one or choose another side!'
	INVALID_ADDRESS = 'Please provide valid wallet address!'
	MISSING_OFFCHAIN = 'Missing offchain data!'

	# OUTCOME
	INVALID_OUTCOME = 'Please check your outcome id'
	OUTCOME_HAS_RESULT = 'This outcome has had result already!'

	# MATCH
	MATCH_NOT_FOUND = 'Match not found. Please try again.'

	# USER
	USER_INVALID_EMAIL = 'Please enter a valid email address.'
	USER_INVALID_INPUT = 'Please make sure your email and password are correct.'
	USER_CANNOT_REGISTRY = 'Sorry, we were unable to register you. Please contact human@autonomous.ai for support.'
	USER_INVALID = 'Invalid user'
	USER_NEED_PURCHASE_PRODUCT = 'Please purchase to sign more.'
	USER_INVALID_ACCESS_TOKEN = 'Invalid user'
	USER_INVALID_SOURCE = 'Please login with google+ or facebook account.'

	# HANSHAKE
	HANDSHAKE_NOT_ENOUGH_GAS = 'You\'re out of gas! Please wait while we add ETH to your account.'
	HANDSHAKE_CANNOT_SEND_TO_MYSELF = 'You can\'t Handshake with yourself!'
	HANDSHAKE_EMPTY = 'This Handshake seems to be empty.'
	HANDSHAKE_NO_PERMISSION = 'You are not authorized to make this Handshake.'
	HANDSHAKE_NO_CONTRACT_FILE = 'Contract file not found!'
	HANDSHAKE_NOT_FOUND = 'Handshake not found. Please try again.'
	HANDSHAKE_TERM_AND_VALUE_NOT_MATCH = 'Please enter a payment amount.'
	HANDSHAKE_VALUE_GREATER_THAN_0 = 'Amount should be larger > 0.'
	HANDSHAKE_AMOUNT_INVALID = 'Amount key is invalid.'
	HANDSHAKE_PUBLIC_INVALID = 'Public key is invalid.'
	HANDSHAKE_INVALID_WALLET_ADDRESS = 'Please enter a valid wallet address which exists in our system.'
	HANDSHAKE_ERROR_ANYTHING = 'You\'re out of gas! Please wait while we add ETH to your account.'
	HANDSHAKE_DESC_TOO_LONG = 'Your note is too long. It should be less than 1000 characters.'
	HANDSHAKE_NO_TYPE = 'Please choose type of handshake.'
	HANDSHAKE_INVALID_BETTING_TYPE = 'This is not betting template.'
	HANDSHAKE_CANNOT_UNINIT = 'There is shakers. Therefore you cannot refund!'

	# SHAKER
	SHAKER_NOT_FOUND = 'Shaker not found. Please try again.'

	# WALLET
	WALLET_EXCEED_FREE_ETH = 'Busy day for Handshakes - we\'re out of freebies! Please try again tomorrow.'
	WALLET_RECEIVE_ETH_ALREADY = 'You can only request free Handshakes once.'
	WALLET_REJECT_FREE_ETH = 'Your account can\'t get free ETH.'
