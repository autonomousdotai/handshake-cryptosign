from app import db
from app.models.base import BaseModel

class User(BaseModel):
	__tablename__ = 'user'
	__json_public__ = ['id', 'fcm_token', 'email']

	fcm_token = db.Column(db.Text)
	payload = db.Column(db.Text)
	email = db.Column(db.String(255))
	free_bet = db.Column(db.Integer,
						server_default=str(0),
						default=0)
	is_subscribe = db.Column(db.Integer,
						server_default=str(1),
						default=1)
	handshakes = db.relationship('Handshake', backref='user', primaryjoin="User.id == Handshake.user_id",
	                             lazy='dynamic')

	@classmethod
	def find_user_with_id(cls, user_id):
		return User.query.filter_by(id=user_id).first()

	def __repr__(self):
		return '<User {}>'.format(self.id)
