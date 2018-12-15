from flask import g
from datetime import *

from app import db
from app.models import Handshake, Shaker
from app.helpers.utils import local_to_utc
from app.tasks import run_bots

import app.constants as CONST


def erc20_save_success_event():
	pass


def run_bots_for_tx(tx, debug=False):
	if tx is not None:
		# Run bots
		if tx.contract_method in ['init', 'shake', 'initTestDrive', 'shakeTestDrive'] and tx.offchain is not None:
			offchain = tx.offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
			if 'm' in offchain:
				offchain = offchain.replace('m', '')
				h = Handshake.find_handshake_by_id(offchain)
				if h is not None:
					if debug:
						return h.outcome_id
					else:
						run_bots.delay(h.outcome_id)

			elif 's' in offchain:
				offchain = offchain.replace('s', '')
				s = Shaker.find_shaker_by_id(offchain)
				if s is not None:
					if debug:
						return s.handshake.outcome_id
					else:
						run_bots.delay(s.handshake.outcome_id)
	return None