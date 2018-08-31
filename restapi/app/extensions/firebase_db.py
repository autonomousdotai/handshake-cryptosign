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
		try:
			print "1111111"
			auth = self.firebase.auth()
			print "2222222"
			db = self.firebase.database()
			print "3333333"
			results = db.child("users").child(user_id).child('betting').push(data)
			print "44444444"
			return results
		except Exception as err:
			print("push_data: %s" % (err))
		
# if __name__ == '__main__':
# 	firebase = FirebaseDatabase()
# 	firebase.push_data({"data": "12"})