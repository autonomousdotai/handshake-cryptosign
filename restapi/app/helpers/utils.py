#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json

from fractions import Fraction
from datetime import datetime


def is_valid_email(email):
	if re.match("^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", email) != None:
		return True
	return False


def is_valid_password(password):
	if len(password) >= 3:
		return True
	return False


def is_valid_name(name):
	if len(name.strip()) == 0:
		return False
	return True


def is_valid_event(data):
	if 'txId' in data and 'txStatus' in data and 'events' in data:
		return True
	return False


def parse_date_to_int(input):
	delta = input - datetime.now()
	return delta.seconds


def isnumber(s):
   try:
     float(s)
     return True
   except ValueError:
     try: 
       Fraction(s)
       return True
     except ValueError: 
       return False

def formalize_description(desc):
	if desc is None or len(desc.strip()) == 0:
		return desc
		
	desc = desc.strip()
	if desc[len(desc)-1] != '.':
		desc = "{}.".format(desc)

	return desc

def parse_str_to_array(shaked_user_ids):
	if shaked_user_ids is None:
		return []
	try:
		data = json.loads(shaked_user_ids)
		if isinstance(data, list):
			return data
		return []
	except Exception as ex:
		print str(ex)
		return []
		
