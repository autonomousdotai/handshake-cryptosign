from app import db
from app.models.base import BaseModel


class Setting(BaseModel):
	__tablename__ = 'setting'
	__json_public__ = ['id', 'name', 'status']

	name = db.Column(db.String(255))
	value = db.Column(db.Text)
	status = db.Column(db.Integer,
	                   server_default=str(0),
	                   default=0)

	@classmethod
	def find_setting_by_id(cls, setting_id):
		return Setting.query.filter_by(id=setting_id).first()

	def __repr__(self):
		return '<Setting {}>'.format(self.id)
