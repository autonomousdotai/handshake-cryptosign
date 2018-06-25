#!/usr/bin/python
# -*- coding: utf-8 -*-

class MESSAGE(object):
	# ERROR
	INVALID_DATA = '1000' 													#'Please double check your input data.'
	INVALID_BET = '1001' 													#'No equivalent bets found. Please create a new bet.'
	INVALID_ADDRESS = '1002' 												#'Please provide valid wallet address!'
	MISSING_OFFCHAIN = '1003' 												#'Missing offchain data!'
	INVALID_ODDS = '1004' 													#'Odds shoule be large than 1'
	MAXIMUM_FREE_BET = '1005' 												#'The maximum free bet is 100!'
	CANNOT_WITHDRAW = '1006' 												#'You cannot withdraw this handshake!'
	CANNOT_ROLLBACK = '1007' 												#'Cannot rollback this handshake!'

	# OUTCOME
	INVALID_OUTCOME = '1008'												#'Please check your outcome id'
	INVALID_OUTCOME_RESULT = '1009'											#'Please check your outcome result'
	OUTCOME_HAS_RESULT = '1010' 											#'This outcome has had result already!'

	# MATCH
	MATCH_NOT_FOUND = '1011'												#'Match not found. Please try again.'
	INVALID_MATCH_RESULT = '1011' 											#'Match result invalid. Please try again.'
	MATCH_RESULT_EMPTY = '1012'												#'Match result is empty. Please try again.'
	MATCH_CANNOT_SET_RESULT = '1013'										#'The report time is exceed!'

	# USER
	USER_INVALID_EMAIL = '1014'												#'Please enter a valid email address.'
	USER_CANNOT_REGISTRY = '1015' 											#'Sorry, we were unable to register you. Please contact human@autonomous.ai for support.'
	USER_INVALID = '1016'													#'Invalid user'
	USER_NEED_PURCHASE_PRODUCT = '1017'										#'Please purchase to sign more.'
	USER_INVALID_ACCESS_TOKEN = '1018' 										#'Invalid user'
	USER_INVALID_SOURCE = '1019' 											#'Please login with google+ or facebook account.'
	USER_RECEIVED_FREE_BET_ALREADY = '1020' 								#'You have received free bet already!'

	# HANSHAKE
	HANDSHAKE_NOT_ENOUGH_GAS = '1021' 										#'You\'re out of gas! Please wait while we add ETH to your account.'
	HANDSHAKE_CANNOT_SEND_TO_MYSELF = '1021' 								#'You can\'t Handshake with yourself!'
	HANDSHAKE_EMPTY = '1022' 												#'This Handshake seems to be empty.'
	HANDSHAKE_NO_PERMISSION = '1023' 										#'You are not authorized to make this Handshake.'
	HANDSHAKE_NO_CONTRACT_FILE = '1024' 									#'Contract file not found!'
	HANDSHAKE_NOT_FOUND = '1025' 											#'Handshake not found. Please try again.'
	HANDSHAKE_TERM_AND_VALUE_NOT_MATCH = '1026' 							#'Please enter a payment amount.'
	HANDSHAKE_VALUE_GREATER_THAN_0 = '1027' 								#'Amount should be larger > 0.'
	HANDSHAKE_AMOUNT_INVALID = '1028' 										#'Amount key is invalid.'
	HANDSHAKE_PUBLIC_INVALID = '1029' 										#'Public key is invalid.'
	HANDSHAKE_INVALID_WALLET_ADDRESS = '1030' 								#'Please enter a valid wallet address which exists in our system.'
	HANDSHAKE_ERROR_ANYTHING = '1031' 										#'You\'re out of gas! Please wait while we add ETH to your account.'
	HANDSHAKE_DESC_TOO_LONG = '1032' 										#'Your note is too long. It should be less than 1000 characters.'
	HANDSHAKE_NO_TYPE = '1033' 												#'Please choose type of handshake.'
	HANDSHAKE_INVALID_BETTING_TYPE = '1034' 								#'This is not betting template.'
	HANDSHAKE_CANNOT_UNINIT = '1035' 										#'There is shakers. Therefore you cannot refund!'
	HANDSHAKE_NOT_THE_SAME_RESULT = '1036' 									#'Your result does not match with outcome!'
	HANDSHAKE_WITHDRAW_AFTER_DISPUTE = '1037' 								#'Withdraw only works after dispute time.'

	# SHAKER
	SHAKER_NOT_FOUND = '1038' 												#'Shaker not found. Please try again.'
	SHAKER_ROLLBACK_ALREADY = '1039' 										#'You have rollbacked already!'


	# WALLET
	WALLET_EXCEED_FREE_ETH = '1040' 										#'Busy day for Handshakes - we\'re out of freebies! Please try again tomorrow.'
	WALLET_RECEIVE_ETH_ALREADY = '1041' 									#'You can only request free Handshakes once.'
	WALLET_REJECT_FREE_ETH = '1042' 										#'Your account can\'t get free ETH.'
