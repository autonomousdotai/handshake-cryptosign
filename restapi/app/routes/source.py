import os
import json
import app.constants as CONST

from flask import Blueprint, request, current_app as app
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required
from app import db
from app.models import Source
from app.helpers.message import MESSAGE, CODE

source_routes = Blueprint('source', __name__)

@source_routes.route('/', methods=['GET'])
@login_required
def sources():
	try:
		sources = Source.query.all()
		data = []

		for source in sources:
			data.append(source.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)


@source_routes.route('/add', methods=['POST'])
@login_required
def add():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		response_json = []
		for item in data:
			source = Source(
				name=item['name'],
				url=item['url']
			)
			db.session.add(source)
			db.session.flush()

			response_json.append(source.to_json())
		db.session.commit()
		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@source_routes.route('/remove/<int:id>', methods=['POST'])
@login_required
def remove(id):
	try:
		source = db.session.query(Source).filter(Source.id==id).first()
		if source is not None:
			db.session.delete(source)
			db.session.commit()
			return response_ok(message="{} has been deleted!".format(source.id))
		else:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@source_routes.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		source = db.session.query(Source).filter(Source.id==id).first()
		if source is not None:
			source.name = data['name']
			source.url = data['url']
			db.session.commit()

			return response_ok(message='{} has been updated'.format(source.id))
		else:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)