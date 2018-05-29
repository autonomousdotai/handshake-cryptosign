from app import db
from app.models.base import BaseModel
import app.constants as CONST
import time

class Handshake(BaseModel):
	__tablename__ = 'handshake'
	__json_public__ = ['id', 'hs_type', 'extra_data', 'chain_id', 'from_address', 'to_address', 'status', 'bk_status', 'description']
	hid = db.Column(db.String(255))
	hs_type = db.Column(db.Integer)
	extra_data = db.Column(db.Text)
	chain_id = db.Column(db.Integer,
						server_default=str(CONST.BLOCKCHAIN_NETWORK['RINKEBY']),
						default=CONST.BLOCKCHAIN_NETWORK['RINKEBY'])
	state = db.Column(db.Integer,
						server_default=str(CONST.COMMUNITY_TYPE['PUBLIC']),
	                   	default=CONST.COMMUNITY_TYPE['PUBLIC'])
	description = db.Column(db.Text)
	from_address = db.Column(db.String(255))
	to_address = db.Column(db.Text)
	status = db.Column(db.Integer,
	                   server_default=str(CONST.Handshake['STATUS_PENDING']),
	                   default=CONST.Handshake['STATUS_PENDING'])
	bk_status = db.Column(db.Integer,
	                      server_default=str(CONST.Handshake['STATUS_PENDING']),
	                      default=CONST.Handshake['STATUS_PENDING'])
	shake_count = db.Column(db.Integer)
	view_count = db.Column(db.Integer)
	shaked_user_ids = db.Column(db.Text)
	secret_key = db.Column(db.String(4096))
	signed_secret_key = db.Column(db.String(4096))

	user_id = db.Column('user_id', db.ForeignKey('user.id'))

	@classmethod
	def find_handshake_by_id(cls, _id):
		handshake = Handshake.query.filter_by(id=_id).first()
		if handshake is not None:
			return handshake
		return None

	@classmethod
	def find_handshake_by_hid(cls, hid):
		handshake = Handshake.query.filter_by(hid=hid).first()
		if handshake is not None:
			return handshake
		return None

	def __repr__(self):
		return '<Handshake [id, hid, hs_type, to_address] {}, {}, {}, [{}]>'.format(self.id, self.hid, self.hs_type, self.to_address)
