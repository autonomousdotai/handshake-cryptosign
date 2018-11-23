import os
import json
import app.constants as CONST
import app.bl.referral as referral_bl

from flask import Blueprint, request, current_app as app
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required
from app import db
from app.models import Referral
from app.helpers.message import MESSAGE, CODE

referral_routes = Blueprint('referral', __name__)

@referral_routes.route('/check', methods=['GET'])
@login_required
def check_referral():
	"""
	" check user has joined referral program or not
	"""
	try:
		uid = int(request.headers['Uid'])
		r = Referral.find_referral_by_uid(uid)

		response = {
			"code": None
		}
		if r is None:
			return response_error(response)

		response['code'] = r.code
		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@referral_routes.route('/join', methods=['GET'])
@login_required
def join_referral_program():
	"""
	" user joins referral program
	"""
	try:
		uid = int(request.headers['Uid'])
		r = Referral.find_referral_by_uid(uid)

		if r is None:
			r = Referral(
				code=referral_bl.generate_referral_code(uid),
				user_id=uid
			)
			db.session.add(r)
			db.session.commit()

			return response_ok(r.to_json())

		return response_error(MESSAGE.REFERRAL_USER_JOINED_ALREADY, CODE.REFERRAL_USER_JOINED_ALREADY)
	except Exception, ex:
		return response_error(ex.message)
