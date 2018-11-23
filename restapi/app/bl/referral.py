import string
import random

from app import db
from app.models import User, Redeem


def generate_referral_code(user_id):
	chars = string.ascii_uppercase + string.ascii_lowercase
	code = '{}{}{}'.format(user_id, string_generator(2), string_num_generator(2))
	return code


def string_generator(size):
	chars = string.ascii_uppercase + string.ascii_lowercase
	return ''.join(random.choice(chars) for _ in range(size))


def string_num_generator(size):
	chars = string.ascii_lowercase + string.digits
	return ''.join(random.choice(chars) for _ in range(size))


def give_redeem_code_for_referred_user(user_id):
	u = User.find_user_with_id(user_id)
	if u is not None and u.invited_by_user is not None and u.invited_by_user > 0:
		redeem = db.session.query(Redeem).filter(Redeem.reserved_id==0, Redeem.used_user==0).limit(1).all()
		if redeem is not None:
			redeem.reserved_id = u.invited_by_user
			db.session.flush()
			
			# TODO: send mail here