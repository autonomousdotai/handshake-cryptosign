from flask import g
from sqlalchemy import and_, func, Date, cast
from datetime import date
from app import db
from app.models import User, Handshake, Shaker
from app.constants import Handshake as HandshakeStatus

def check_user_is_able_to_create_new_free_bet():
	data = db.session.query(func.sum(User.free_bet).label('amount')).filter(cast(User.date_created,Date) == date.today()).first()
	if data[0] is not None and int(data[0]) >= 100:
		return False
	return True

def count_user_free_bet(user_id):
	# hs_count = db.session.query(func.count(Handshake.id)).filter(Handshake.free_bet == 1, Handshake.user_id == user_id, Handshake.status.in_([HandshakeStatus['STATUS_DONE'], HandshakeStatus['STATUS_SHAKER_SHAKED'], HandshakeStatus['STATUS_INITED']])).scalar()
	# s_count = db.session.query(func.count(Shaker.id)).filter(Shaker.free_bet == 1, Shaker.shaker_id == user_id, Shaker.status.in_([HandshakeStatus['STATUS_DONE'], HandshakeStatus['STATUS_SHAKER_SHAKED'], HandshakeStatus['STATUS_INITED']])).scalar()
	hs_count = db.session.query(func.count(Handshake.id)).filter(Handshake.free_bet == 1, Handshake.user_id == user_id).scalar()
	s_count = db.session.query(func.count(Shaker.id)).filter(Shaker.free_bet == 1, Shaker.shaker_id == user_id).scalar()
	return (hs_count if hs_count is not None else 0) + (s_count if s_count is not None else 0)