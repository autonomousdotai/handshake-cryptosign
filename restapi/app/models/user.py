from app import db
from app.models.base import BaseModel

class User(BaseModel):
	__tablename__ = 'user'
	__json_public__ = ['id', 'uid']
	uid = db.Column(db.BigInteger)
	handshakes = db.relationship('Handshake', backref='user', primaryjoin="User.id == Handshake.user_id",
	                             lazy='dynamic')
	txs = db.relationship('Tx', backref='user', primaryjoin="User.id == Tx.user_id", lazy='dynamic')

	@classmethod
	def find_user_with_id(cls, user_id):
		user = User.query.filter_by(id=user_id).first()
		if user is not None:
			return user
		return None

	@classmethod
	def find_user_with_uid(cls, uid):
		user = User.query.filter_by(uid=uid).first()
		if user is not None:
			return user
		return None

	def __repr__(self):
		return '<User {}>'.format(self.id)
