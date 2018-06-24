from flask import g
from sqlalchemy import and_, func, Date, cast
from datetime import date
from app import db
from app.models import User


def check_user_is_able_to_create_new_free_bet():
	data = db.session.query(func.sum(User.free_bet).label('amount')).filter(cast(User.date_created,Date) == date.today()).first()
	if data[0] is not None and int(data[0]) >= 100:
		return False
	return True