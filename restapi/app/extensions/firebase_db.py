import pyrebase
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

config = {
	"apiKey": "",
	"authDomain": "",
	"databaseURL": "",
	"storageBucket": "",
	"serviceAccount": dir_path + "/handshake-205007.json"
}
class FirebaseDatabase(object):
	def __init__(self, app=None):
		super(FirebaseDatabase, self).__init__()
		if app:
			self.app = app
			config['databaseURL'] = app.config['FIREBASE_DATABASE_URL']
			self.firebase = pyrebase.initialize_app(config)
			
	def init_app(self, app):
		self.app = app
		config['databaseURL'] = app.config['FIREBASE_DATABASE_URL']
		self.firebase = pyrebase.initialize_app(config)

	def push_data(self, data, user_id):
		auth = self.firebase.auth()
		db = self.firebase.database()
		results = db.child("users").child(user_id).child('betting').push(data)

		
# if __name__ == '__main__':
# 	firebase = FirebaseDatabase()
# 	firebase.push_data({"data": "12"})