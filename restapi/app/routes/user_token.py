import os
import json
import app.constants as CONST

from flask import Blueprint, request, g, current_app as app
from flask_jwt_extended import jwt_required
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required
from app import db
from app.models import UserToken, User, Token
from app.helpers.message import MESSAGE, CODE


user_token_routes = Blueprint('user-token', __name__)

@user_token_routes.route('/', methods=['GET'])
@login_required
def user_tokens():
	try:
		uid = int(request.headers['Uid'])
		user = User.find_user_with_id(uid)
		user_tokens = db.session.query(UserToken).filter(UserToken.user_id==uid).all()

		data = []
		for item in user_tokens:
			data.append(item.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)

@user_token_routes.route('/add', methods=['POST'])
@login_required
def add():
	try:
		uid = int(request.headers['Uid'])
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)
		token = Token.find_token_by_id(data["token_id"])
		if token is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		ut = UserToken(
			user_id=uid,
			hash=data["hash"],
			address=data["address"],
			token_id=data["token_id"],
			status=CONST.USER_TOKEN_STATUS['PENDING']
		)
		db.session.add(ut)
		db.session.flush()	
		db.session.commit()

		return response_ok(ut.to_json())
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
