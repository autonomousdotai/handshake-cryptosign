# -*- coding: utf-8 -*-
import os
import sys
import json
import hashlib
import requests

from flask import Blueprint, request, g
from app import db
from app.models import User
from flask_jwt_extended import (create_access_token)

from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import service_required
from app.helpers.response import response_ok, response_error

hook_routes = Blueprint('hook', __name__)

@hook_routes.route('/dispatcher', methods=['POST'])
@service_required
def user_hook():
	try:
		data = request.json
		print "Hook data: {}".format(data)
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		type_change = data.get('type_change', None)
		user_id = data.get('user_id', None)
		email = data.get('email', None)
		meta_data = data.get('meta_data', None)

		if type_change == "Update":
			user = User.find_user_with_id(user_id)
			
			if user is not None and user.email != email and email is not None and email != "":
				print "Update email: {}".format(email)
				user.email = email
				db.session.commit()

		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
