import pyrebase


class FirebaseDatabase(object):
	def __init__(self, app=None):
		super(FirebaseDatabase, self).__init__()
		if app:
			self.app = app
			self.firebase = pyrebase.initialize_app(config)
			
	def init_app(self, app):
		self.app = app
		self.firebase = pyrebase.initialize_app(self.config)

	def push_data(self, data):
		auth = self.firebase.auth()
		user = auth.sign_in_with_email_and_password("handshake@autonomous.nyc", "123456")
		db = self.firebase.database()
		results = db.child("users").push(data, user['idToken'])

		
# if __name__ == '__main__':
# 	firebase = FirebaseDatabase()
# 	firebase.push_data({"data": "1"})