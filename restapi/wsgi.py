from werkzeug.serving import run_simple
from flask_socketio import SocketIO

import sys
from app import app as application

reload(sys)
sys.setdefaultencoding('utf-8')

socketio = SocketIO(application)

if __name__ == "__main__":
	# socketio.run(application)
	run_simple('0.0.0.0', 5000, socketio, use_reloader=True, use_debugger=True, threaded=True)
