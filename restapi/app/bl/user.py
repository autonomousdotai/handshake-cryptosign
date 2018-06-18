from flask import g
from sqlalchemy import and_, func, Date, cast
from datetime import datetime

from app import db
from app.models import User, Handshake
from app.helpers.message import MESSAGE
from datetime import date

import app.constants as CONST
import requests
import json
import base64
import hashlib
import urllib


def check_user_is_able_to_create_new_handshake(user):
	delta = datetime.now() - user.subscription_date
	if delta.days > 30:
		return MESSAGE.USER_NEED_PURCHASE_PRODUCT
	else:
		handshakes = db.session.query(Handshake).filter(and_(Handshake.user_id==user.id, Handshake.date_created>=user.subscription_date, Handshake.date_created<=datetime.now())).all()
		if len(handshakes) >= user.subscription_type:
			return MESSAGE.USER_NEED_PURCHASE_PRODUCT
	return ''


def check_user_is_able_to_create_new_free_bet():
	data = db.session.query(func.sum(User.free_bet).label('amount')).filter(cast(User.date_created,Date) == date.today()).first()
	if int(data[0]) >= 100:
		return False
	return True