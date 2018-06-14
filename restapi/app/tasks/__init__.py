import sys
from flask import Flask
from werkzeug.datastructures import FileStorage

from app.factory import make_celery
from app.core import db, s3, configure_app, wm, ipfs, firebase
from app.extensions.file_crypto import FileCrypto
from app.models import Handshake, Outcome, User, Shaker

import time
import app.constants as CONST
import simplejson as json
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
# init firebase database
firebase.init_app(app)

# celery
celery = make_celery(app)


@celery.task()
def update_feed(handshake_id, shake_id=-1):
	try:
		handshake = Handshake.find_handshake_by_id(handshake_id)
		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
		if outcome is None:
			print 'outcome is None'
			return
		
		print '------------------------------------------------'
		print 'update feed for user id: {}'.format(handshake.user_id)
		print '------------------------------------------------'
		shaker = None

		# create maker id
		_id = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(handshake.id)
		amount = handshake.amount
		status = handshake.status
		bk_status = handshake.bk_status
		shakers = handshake.shakers

		shake_user_ids = []
		shake_user_infos = []
		if shakers is not None:
			for s in shakers:
				shake_user_ids.append(s.shaker_id)	
				shake_user_infos.append(s.to_json())

		if shake_id != -1:
			shaker = Shaker.find_shaker_by_id(shake_id)
			if shaker is not None:
				if shaker.shaker_id not in shake_user_ids:
					shake_user_ids.append(shaker.shaker_id)
					shake_user_infos.append(shaker.to_json())

		extra_data = {}
		try:
			extra_data = json.loads(handshake.extra_data)
		except Exception as ex:
			print 'Handshake has no extra data'
		extra_data['shakers'] = shake_user_infos

		hs = {
			"id": _id,
			"hid_s": outcome.hid,
			"type_i": handshake.hs_type,
			"state_i": handshake.state,
			"status_i": status,
			"bk_status_i": bk_status,
			"init_user_id_i": handshake.user_id,
			"chain_id_i": handshake.chain_id,
			"shake_user_ids_is": shake_user_ids,
			"text_search_ss": [handshake.description],
			"shake_count_i": handshake.shake_count,
			"view_count_i": handshake.view_count,
			"comment_count_i": 0,
			"init_at_i": int(time.mktime(handshake.date_created.timetuple())),
			"last_update_at_i": int(time.mktime(handshake.date_modified.timetuple())),
			"is_private_i": handshake.is_private,
			"extra_data_s": json.dumps(extra_data, use_decimal=True),
			"remaining_amount_f": float(handshake.remaining_amount),
			"amount_f": float(amount),
			"outcome_id_i": handshake.outcome_id,
			"odds_f": float(handshake.odds),
			"currency_s": handshake.currency,
			"side_i": handshake.side,
			"from_address_s": handshake.from_address,
			"result_i": outcome.result
		}
		print 'create maker {}'.format(hs)

		# add to firebase database
		firebase.push_data(hs, handshake.user_id)

		#  add to solr
		arr_handshakes = []
		arr_handshakes.append(hs)
		endpoint = "{}/handshake/update".format(app.config['SOLR_SERVICE'])
		data = {
			"add": arr_handshakes
		}
		res = requests.post(endpoint, json=data)
		if res.status_code > 400:
			print('SOLR service is failed.')


	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("add_feed=>",exc_type, fname, exc_tb.tb_lineno)
