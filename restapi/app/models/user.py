from app import db
from app.models.base import BaseModel

class User(BaseModel):
	__tablename__ = 'user'
	__json_public__ = ['id', 'fcm_token']

	fcm_token = db.Column(db.Text)
	payload = db.Column(db.Text)
	free_bet = db.Column(db.Integer,
						server_default=str(0),
						default=0)
	handshakes = db.relationship('Handshake', backref='user', primaryjoin="User.id == Handshake.user_id",
	                             lazy='dynamic')

	@classmethod
	def find_user_with_id(cls, user_id):
		user = User.query.filter_by(id=user_id).first()
		if user is not None:
			return user
		return None

	def __repr__(self):
		return '<User {}>'.format(self.id)
