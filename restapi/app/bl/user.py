from flask import g
from sqlalchemy import and_, func
from datetime import datetime

from app import db
from app.models import User, Handshake
from app.helpers.message import MESSAGE

import app.constants as CONST
import requests
import json
import base64
import hashlib
import urllib


def isUserHasWalletOnMainNetwork(user):
	if  user.wallets.filter_by(source='Both').first() is None:
		if user.wallets.filter_by(source='Main Network').first() is None:
			return False
	return True

def autonomous_social_login(source, access_token):
	endpoint = "{}/customer-api/social/auth?type=handshake&source={}&access_token={}".format(
		g.AUTONOMOUS_SERVICE_ENDPOINT, urllib.quote_plus(source), access_token)
	res = requests.get(endpoint)
	if res.status_code > 400:
		raise Exception('Autonomous API social login failed.')
	json = res.json()
	return json


def autonomous_verify_email(email):
	endpoint = "{}/customer-api/verify-email?email={}".format(g.AUTONOMOUS_SERVICE_ENDPOINT, email)
	res = requests.get(endpoint)
	if res.status_code > 400:
		raise Exception('Autonomous API verify email failed.')
	json = res.json()
	return json


def autonomous_verify_email2(email):
	endpoint = "{}/customer-api/verify-email?email={}&ignore_eth=true".format(g.AUTONOMOUS_SERVICE_ENDPOINT, email)
	res = requests.get(endpoint)
	if res.status_code > 400:
		raise Exception('Autonomous API verify email 2 failed.')
	json = res.json()
	return json


def autonomous_forgot_password(email):
	endpoint = "{}/customer-api/reset-password-request?email={}".format(g.AUTONOMOUS_SERVICE_ENDPOINT, email)
	res = requests.post(endpoint)
	if res.status_code > 400:
		raise Exception('Autonomous API forgot password failed.')
	json = res.json()
	return json


def autonomous_free_handshake_beta(email):
	endpoint = "{}/customer-api/check-free-hanshake-beta-user?email={}".format(g.AUTONOMOUS_SERVICE_ENDPOINT, email)
	res = requests.get(endpoint)
	if res.status_code > 400:
		raise Exception('Autonomous API check free handshake beta user failed.')
	json = res.json()
	return json


def autonomous_update_user_info(user):
	key = hashlib.md5('{}.{}'.format(g.AUTONOMOUS_WEB_PASSPHASE, user.ref_id)).hexdigest()
	endpoint = "{}/customer-api/ext/update/{}?fullname={}&key={}".format(g.AUTONOMOUS_SERVICE_ENDPOINT, user.ref_id, user.name, str(key))

	# print endpoint
	res = requests.put(endpoint)

	if res.status_code > 400:
		raise Exception('Autonomous API update user profile failed.')
	json = res.json()
	return json


def autonomous_sign_in(email, password):
	endpoint = "{}/customer-api/sign-in?type=handshake".format(g.AUTONOMOUS_SERVICE_ENDPOINT)
	params = {
        'email': email,
        'password': base64.b64encode(password)
    }
	res = requests.post(endpoint, json=params)
	if res.status_code > 400:
		raise Exception('Autonomous API sign in failed.')
	json = res.json()
	return json

def autonomous_auth_user(email, password):
	endpoint = "{}/customer-api/userinfo-by-auth".format(g.AUTONOMOUS_SERVICE_ENDPOINT)
	params = {
        'email': email,
        'password': base64.b64encode(password)
    }
	res = requests.post(endpoint, json=params)
	if res.status_code > 400:
		raise Exception('Autonomous API get user info failed.')
	json = res.json()
	return json


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
	users = db.session.query(User).filter(and_(Handshake.free_bet==1)).all()
	if len(users) > 100:
		return False
	return True