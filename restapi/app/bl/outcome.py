#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json

from app.helpers.bc_exception import BcException
from flask import g

def init_default_outcomes(start, end, outcome_data):
	bc_res = requests.post(g.BLOCKCHAIN_SERVER_ENDPOINT + '/cryptosign/odds/init?start={}&end={}'.format(start, end),
							json=outcome_data,
							headers={"Content-Type": "application/json"})
	bc_json = bc_res.json()
	print "bc_json=>", bc_json
	if bc_json['status'] != 1:
		raise BcException(bc_json['message'])