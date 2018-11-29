import string
import random

from flask import g
from app import db
from app.models import User, Redeem, Referral
from app.tasks import send_reward_redeem
from app.helpers.utils import is_valid_email


def generate_referral_code(user_id):
	chars = string.ascii_uppercase + string.ascii_lowercase
	code = '{}{}{}'.format(user_id, string_generator(2), string_num_generator(2))
	return code


def issue_referral_code_for_user(user):
	r = Referral.find_referral_by_uid(user.id)
	if r is None:
		code = generate_referral_code(user.id)
		r = Referral(
			code=code,
			user_id=user.id
		)
		db.session.add(r)
		db.session.flush()

	return r.code


def string_generator(size):
	chars = string.ascii_uppercase + string.ascii_lowercase
	return ''.join(random.choice(chars) for _ in range(size))


def string_num_generator(size):
	chars = string.ascii_lowercase + string.digits
	return ''.join(random.choice(chars) for _ in range(size))


def give_redeem_code_for_referred_user(user_id):
	"""
	" Give redeem code for user who invites user_id
	"""
	u = User.find_user_with_id(user_id)
	print '1'
	if u is not None and u.invited_by_user is not None and u.invited_by_user > 0:
		print '2'
		redeem = db.session.query(Redeem).filter(Redeem.reserved_id==0, Redeem.used_user==0).limit(1).all()
		if redeem is not None:
			print '3'
			redeem.reserved_id = u.invited_by_user
			db.session.flush()
			
			# send mail to invited user to inform new redeem code
			print 'BEGIN'
			reward_user_redeem_code(u.invited_by_user, redeem.code)		
			print 'END'


def reward_user_redeem_code(user_id, code):
	print 'DEBUG 1'
	u = User.find_user_with_id(user_id)
	if u is not None and is_valid_email(u.email):
		print 'DEBUG {} {}'.format(g.BASE_URL, code)
		send_reward_redeem.delay(u.email, code, '{}prediction?refer={}'.format(g.BASE_URL, code))
		print 'DEBUG 3'

def is_user_can_join_referral_program(user):
	r = Referral.find_referral_by_uid(user.id)
	if is_valid_email(user.email) and r is None:
		return True

	return False