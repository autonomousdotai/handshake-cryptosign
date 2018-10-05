# -*- coding: utf-8 -*-
import os
import sys
import json
import hashlib
import requests
import app.bl.user as user_bl

from flask import Blueprint, request, g
from app import db
from app.models import User, Handshake, Shaker, Outcome
from datetime import datetime

from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import login_required
from app.helpers.response import response_ok, response_error
from app.constants import Handshake as HandshakeStatus

reputation_routes = Blueprint('reputation', __name__)


@reputation_routes.route('/user/<int:user_id>', methods=['GET'])
@login_required
def get_reputation_user(user_id):
	try:
		user = User.find_user_with_id(user_id)
		if user is None:
			return response_error(MESSAGE.USER_INVALID, CODE.USER_INVALID)

		# get all outcome created by user_id
		disputed_status = [HandshakeStatus['STATUS_DISPUTE_PENDING'], HandshakeStatus['STATUS_USER_DISPUTED'], HandshakeStatus['STATUS_DISPUTED']]
		outcomes = db.session.query(Outcome)\
			.filter(Outcome.hid != None)\
			.filter(Outcome.created_user_id == user_id)\
			.all()

		outcome_ids = list(map(lambda x: x.id, outcomes))
		print outcome_ids
		# get all bet of outcome created by user_id
		hs_all_bets = db.session.query(Handshake.user_id.label("user_id"), Handshake.status.label("status"), Handshake.amount)\
			.filter(Handshake.outcome_id.in_(outcome_ids))

		s_all_bets = db.session.query(Shaker.shaker_id.label("user_id"), Shaker.status.label("status"), Shaker.amount)\
			.filter(Shaker.handshake_id == Handshake.id)\
			.filter(Handshake.outcome_id.in_(outcome_ids))

		data_response = {}

		bets_result = hs_all_bets.union_all(s_all_bets).all()

		data_response['total_events'] = len(outcome_ids)
		data_response['total_bets'] = len(bets_result)
		data_response['total_amount'] = sum(float(amount) for user_id,status,amount in bets_result)

		disputed_bets = list(filter(lambda x: x.status in disputed_status, bets_result))

		data_response['total_disputed_bets'] = len(disputed_bets)
		data_response['total_disputed_events'] = len(list(filter(lambda x: x.result == -3, outcomes)))
		data_response['total_disputed_amount'] = sum(float(amount) for user_id,status,amount in disputed_bets)

		return response_ok(data_response)

	except Exception, ex:
		return response_error(ex.message)
