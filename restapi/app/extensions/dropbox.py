import app.constants as CONST

from dropbox import Dropbox

class Dropbox(object):
	def __init__(self, app=None):
		super(Dropbox, self).__init__()
		if app:
			self.app = app
			self.dropbox = Dropbox(app.config['DROPBOX_ACCESS_TOKEN'])

	def init_app(self, app):
		self.app = app
		self.dropbox = Dropbox(app.config['DROPBOX_ACCESS_TOKEN'])

	def upload(self, from_file_path, to_file_path):
		with open(from_file_path, 'rb') as f:
            self.dropbox.files_upload(f.read(), to_file_path, mode=WriteMode('overwrite'))