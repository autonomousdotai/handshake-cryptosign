import pyrebase
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

config = {
	"apiKey": "",
	"authDomain": "",
	"databaseURL": "",
	"storageBucket": "",
	"serviceAccount": ""
}
class FirebaseDatabase(object):
	def __init__(self, app=None):
		super(FirebaseDatabase, self).__init__()
		if app:
			self.app = app
			config['databaseURL'] = app.config['FIREBASE_DATABASE_URL']
			config['serviceAccount'] = dir_path + "/{}.json".format(app.config['FIREBASE_PROJECT_NAME'])
			self.firebase = pyrebase.initialize_app(config)
			
	def init_app(self, app):
		self.app = app
		config['databaseURL'] = app.config['FIREBASE_DATABASE_URL']
		config['serviceAccount'] = dir_path + "/{}.json".format(app.config['FIREBASE_PROJECT_NAME'])
		self.firebase = pyrebase.initialize_app(config)

	def push_data(self, data, user_id):
		auth = self.firebase.auth()
		db = self.firebase.database()
		results = db.child("users").child(user_id).child('betting').push(data)
		return results

		
# if __name__ == '__main__':
# 	firebase = FirebaseDatabase()
# 	firebase.push_data({"data": "12"})