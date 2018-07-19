#!/usr/bin/python
# -*- coding: utf-8 -*-

class MESSAGE(object):
	# ERROR
	INVALID_DATA = 'Please double check your input data.'
	INVALID_BET = 'No equivalent bets found. Please create a new bet.'
	INVALID_ADDRESS = 'Please provide valid wallet address!'
	MISSING_OFFCHAIN = 'Missing offchain data!'
	INVALID_ODDS = 'Odds shoule be large than 1'
	MAXIMUM_FREE_BET = 'The maximum free bet is 100!'
	CANNOT_WITHDRAW = 'You cannot withdraw this handshake!'
	CANNOT_ROLLBACK = 'Cannot rollback this handshake!'

	# OUTCOME
	OUTCOME_INVALID = 'Please check your outcome id'
	OUTCOME_INVALID_RESULT = 'Please check your outcome result'
	OUTCOME_HAS_RESULT = 'This outcome has had result already!'
	OUTCOME_REPORTED = 'This outcome reported!'
	OUTCOME_DISPUTE_INVALID = 'This outcome dispute invalid!'

	# MATCH
	MATCH_NOT_FOUND = 'Match not found. Please try again.'
	MATCH_INVALID_RESULT = 'Match result invalid. Please try again.'
	MATCH_RESULT_EMPTY = 'Match result is empty. Please try again.'
	MATCH_CANNOT_SET_RESULT = 'The report time is exceed!'
	MATCH_INVALID_TIME = 'Please double check your closing time, report time and dispute time'

	# USER
	USER_INVALID_EMAIL = 'Please enter a valid email address.'
	USER_CANNOT_REGISTRY = 'Sorry, we were unable to register you. Please contact human@autonomous.ai for support.'
	USER_INVALID = 'Invalid user'
	USER_NEED_PURCHASE_PRODUCT = 'Please purchase to sign more.'
	USER_INVALID_ACCESS_TOKEN = 'Invalid user'
	USER_INVALID_SOURCE = 'Please login with google+ or facebook account.'
	USER_RECEIVED_FREE_BET_ALREADY = 'You have received free bet already!'

	# HANSHAKE
	HANDSHAKE_NOT_ENOUGH_GAS = 'You\'re out of gas! Please wait while we add ETH to your account.'
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
	HANDSHAKE_CANNOT_UNINIT = 'There is an error happens or you are calling cancel too fast. Need wait for 5 minutes!'
	HANDSHAKE_NOT_THE_SAME_RESULT = 'Your result does not match with outcome!'
	HANDSHAKE_WITHDRAW_AFTER_DISPUTE = 'Withdraw only works after dispute time.'
	HANDSHAKE_CANNOT_REFUND = 'Cannot refund this handshake!'

	# SHAKER
	SHAKER_NOT_FOUND = 'Shaker not found. Please try again.'
	SHAKER_ROLLBACK_ALREADY = 'You have rollbacked already!'


	# WALLET
	WALLET_EXCEED_FREE_ETH = 'Busy day for Handshakes - we\'re out of freebies! Please try again tomorrow.'
	WALLET_RECEIVE_ETH_ALREADY = 'You can only request free Handshakes once.'
	WALLET_REJECT_FREE_ETH = 'Your account can\'t get free ETH.'

	# TOKEN
	TOKEN_NOT_FOUND = 'Token not found. Please try again.'


	# NOTIFICATION
	NOTIF_TIME_INVALID = 'Notification time is invalid.'
	NOTIF_INVALID = 'Please check your notif id'


class CODE(object):
	# ERROR
	INVALID_DATA = '1000' 													
	INVALID_BET = '1001' 													
	INVALID_ADDRESS = '1002' 												
	MISSING_OFFCHAIN = '1003' 												
	INVALID_ODDS = '1004' 													
	MAXIMUM_FREE_BET = '1005' 												
	CANNOT_WITHDRAW = '1006' 												
	CANNOT_ROLLBACK = '1007' 												

	# OUTCOME
	OUTCOME_INVALID = '1008'												
	OUTCOME_INVALID_RESULT = '1009'											
	OUTCOME_HAS_RESULT = '1010' 											

	# MATCH
	MATCH_NOT_FOUND = '1011'												
	MATCH_INVALID_RESULT = '1011' 											
	MATCH_RESULT_EMPTY = '1012'												
	MATCH_CANNOT_SET_RESULT = '1013'	
	MATCH_INVALID_TIME = '1043'									

	# USER
	USER_INVALID_EMAIL = '1014'												
	USER_CANNOT_REGISTRY = '1015' 											
	USER_INVALID = '1016'													
	USER_NEED_PURCHASE_PRODUCT = '1017'										
	USER_INVALID_ACCESS_TOKEN = '1018' 										
	USER_INVALID_SOURCE = '1019' 											
	USER_RECEIVED_FREE_BET_ALREADY = '1020' 								

	# HANSHAKE
	HANDSHAKE_NOT_ENOUGH_GAS = '1021'	
	HANDSHAKE_EMPTY = '1022' 												
	HANDSHAKE_NO_PERMISSION = '1023' 										
	HANDSHAKE_NO_CONTRACT_FILE = '1024' 									
	HANDSHAKE_NOT_FOUND = '1025' 											
	HANDSHAKE_TERM_AND_VALUE_NOT_MATCH = '1026' 							
	HANDSHAKE_VALUE_GREATER_THAN_0 = '1027' 								
	HANDSHAKE_AMOUNT_INVALID = '1028' 										
	HANDSHAKE_PUBLIC_INVALID = '1029' 										
	HANDSHAKE_INVALID_WALLET_ADDRESS = '1030' 								
	HANDSHAKE_ERROR_ANYTHING = '1031' 										
	HANDSHAKE_DESC_TOO_LONG = '1032' 										
	HANDSHAKE_NO_TYPE = '1033' 												
	HANDSHAKE_INVALID_BETTING_TYPE = '1034' 								
	HANDSHAKE_CANNOT_UNINIT = '1035' 										
	HANDSHAKE_NOT_THE_SAME_RESULT = '1036' 									
	HANDSHAKE_WITHDRAW_AFTER_DISPUTE = '1037' 	
	HANDSHAKE_CANNOT_REFUND = '1044'							

	# SHAKER
	SHAKER_NOT_FOUND = '1038' 												
	SHAKER_ROLLBACK_ALREADY = '1039' 										


	# WALLET
	WALLET_EXCEED_FREE_ETH = '1040' 										
	WALLET_RECEIVE_ETH_ALREADY = '1041' 									
	WALLET_REJECT_FREE_ETH = '1042' 										

	# NOTIF
	NOTIF_INVALID = '1100'

	# TOKEN
	TOKEN_NOT_FOUND = '1045'
	
