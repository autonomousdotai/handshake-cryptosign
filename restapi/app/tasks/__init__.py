import sys
from flask import Flask
from werkzeug.datastructures import FileStorage

from app.factory import make_celery
from app.core import db, s3, configure_app, wm, ipfs
from app.extensions.file_crypto import FileCrypto
from app.models import Handshake

import time
import app.constants as CONST
import json
import os, hashlib
import requests

app = Flask(__name__)
# config app
configure_app(app)

# db
db.init_app(app)
# s3
s3.init_app(app)
# init ipfs
ipfs.init_app(app)

#
celery = make_celery(app)


@celery.task()
def add_transaction():
	try:
		pass
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("add_transaction=>",exc_type, fname, exc_tb.tb_lineno)