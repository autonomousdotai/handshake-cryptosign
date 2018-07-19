import os
import json
import app.constants as CONST

from flask import Blueprint, request, current_app as app
from flask_jwt_extended import jwt_required
from sqlalchemy import and_
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required
from app import db
from app.models import Token, Task
from app.helpers.message import MESSAGE, CODE

token_routes = Blueprint('token', __name__)

@token_routes.route('/', methods=['GET'])
@login_required
def tokens():
	try:
		tokens = db.session.query(Token).filter(and_(Token.status==CONST.TOKEN_STATUS['APPROVED'], Token.deleted==0)).all()
		data = []
		for token in tokens:
			data.append(token.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)


@token_routes.route('/add', methods=['POST'])
@login_required
def add():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		response_json = []
		for item in data:
			token = Token(
				symbol=item['symbol'],
				name=item['name'],
				decimal=int(item['decimal'])
			)
			db.session.add(token)
			db.session.flush()

			response_json.append(token.to_json())

		db.session.commit()
		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@token_routes.route('/remove/<int:id>', methods=['POST'])
@jwt_required
def remove(id):
	try:
		token = db.session.query(Token).filter(Token.id==id).first()
		if token is not None:
			token.deleted = 1
			db.session.commit()
		else:
			return response_error(MESSAGE.TOKEN_NOT_FOUND, CODE.TOKEN_NOT_FOUND)

		return response_ok(message="{} has been deleted!".format(token.name))
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@token_routes.route('/approve/<int:id>', methods=['GET'])
@jwt_required
def approve(id):
	try:
		# set status = 1
		# call bc: add new token
		token = db.session.query(Token).filter(Token.id==id).first()
		if token is None:
			return response_error(MESSAGE.TOKEN_NOT_FOUND, CODE.TOKEN_NOT_FOUND)
			
		token.status = 1
		db.session.merge(token)

		task = Task(
					task_type=CONST.TASK_TYPE['ERC_20'],
					data=json.dumps(token.to_json()),
					action=CONST.TASK_ACTION['ADD_TOKEN'],
					status=-1
				)
		db.session.add(task)
		db.session.commit()

		return response_ok(message="{} has been approved!".format(token.name))
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)