import os
import json
import app.constants as CONST

from flask import Blueprint, request, current_app as app
from sqlalchemy import and_
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import admin_required
from app import db
from app.models import Redeem
from app.helpers.message import MESSAGE, CODE

redeem_routes = Blueprint('redeem', __name__)


@redeem_routes.route('/add', methods=['POST'])
@admin_required
def add():
	try:
		redeem_path = os.path.abspath(os.path.dirname(__file__)) + '/redeem.txt'
		data = None
		with open(redeem_path, 'r') as f:
			data = f.readlines()
		
		if data is not None:
			data = [x.strip() for x in data] 
			for code in data:
				r = Redeem.find_redeem_by_code(code)
				if r is None:
					r = Redeem(
						code=code
					)
					db.session.add(r)
			db.session.commit()
		
		return response_ok(data)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
