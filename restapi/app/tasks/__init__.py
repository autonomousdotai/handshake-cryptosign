from flask import Flask
from app.factory import make_celery
from app.core import db, configure_app, firebase
from app.models import Handshake, Outcome, Shaker, Match, Task
from app.helpers.utils import utc_to_local
from sqlalchemy import and_
from decimal import *
from datetime import datetime
from requests_toolbelt.multipart.encoder import MultipartEncoder

import sys
import time
import app.constants as CONST
import simplejson as json
import os, hashlib
import requests
import random
import app.bl.task as task_bl

app = Flask(__name__)
# config app
configure_app(app)

# db
db.init_app(app)

# init firebase database
firebase.init_app(app)

# celery
celery = make_celery(app)


@celery.task()
def update_feed(handshake_id):
	try:
		handshake = Handshake.find_handshake_by_id(handshake_id)
		if handshake is None:
			print 'handshake {} is None'.format(handshake_id)
			return

		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
		if outcome is None:
			print 'outcome for handshake: {} is None'.format(handshake_id)
			return

		match = Match.find_match_by_id(outcome.match_id)
		if match is None:
			print 'match is None'
			return
		
		print '-----------------------------------------------------------'
		print 'begin: update feed for user id: {}'.format(handshake.user_id)
		print '-----------------------------------------------------------'

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
			"init_at_i": int(time.mktime(handshake.date_created.timetuple())),
			"last_update_at_i": int(time.mktime(handshake.date_modified.timetuple())),
			"is_private_i": handshake.is_private,
			"extra_data_s": handshake.extra_data,
			"remaining_amount_f": float(handshake.remaining_amount),
			"amount_f": float(amount),
			"outcome_id_i": handshake.outcome_id,
			"odds_f": float(handshake.odds),
			"currency_s": handshake.currency,
			"side_i": handshake.side,
			"from_address_s": handshake.from_address,
			"result_i": outcome.result,
			"free_bet_i": handshake.free_bet,
			"shakers_s": json.dumps(shake_user_infos, use_decimal=True),
			"closing_time_i": match.date,
			"reporting_time_i": match.reportTime,
			"disputing_time_i": match.disputeTime,
			"outcome_total_amount_s": '{0:f}'.format(outcome.total_amount if outcome.total_amount is not None else 0),
			"outcome_total_dispute_amount_s": '{0:f}'.format(outcome.total_dispute_amount if outcome.total_dispute_amount is not None else 0),
			"contract_address_s": handshake.contract_address,
			"contract_json_s": handshake.contract_json
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
		if res.status_code > 400 or \
			res.content is None or \
			(isinstance(res.content, str) and 'null' in res.content):
			print('SOLR service is failed. Save to task')
			task = Task(
						task_type=CONST.TASK_TYPE['NORMAL'],
						data=json.dumps(hs),
						action=CONST.TASK_ACTION['ADD_FEED'],
						status=-1
					)
			db.session.add(task)
			db.session.commit()

	except Exception as e:
		db.session.rollback()
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("add_feed=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def add_shuriken(user_id, shuriken_type):
	try:
		if user_id is not None:
			endpoint = "{}/api/system/betsuccess/{}".format(app.config['DISPATCHER_SERVICE_ENDPOINT'], user_id)
			params = {
				"type": str(shuriken_type)
			}
			res = requests.post(endpoint, params=params)
			print 'add_shuriken {}'.format(res)
			if res.status_code > 400:
				print('Add shuriken is failed.')


	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("add_shuriken=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def run_bots(outcome_id):
	try:
		# find all handshakes of this outcome on both 2 sides: support and oppose
		# if there is a handshake which is not bot and amount < 0.1 then match it
		# otherwise
		# get last odds of this outcome and create handshake with that odds

		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is None or outcome.result != -1 or outcome.hid is None:
			return
		

		print '---------------------------------'
		print '--------- run bots --------------'
		arr_support_hs = db.session.query(Handshake).filter(and_(Handshake.status==CONST.Handshake['STATUS_INITED'], Handshake.side==CONST.SIDE_TYPE['SUPPORT'], Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0)).all()
		arr_oppose_hs = db.session.query(Handshake).filter(Handshake.status==CONST.Handshake['STATUS_INITED'], Handshake.side==CONST.SIDE_TYPE['AGAINST'], Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0).all()

		support_odds = ['1.2', '1.5', '1.6']
		oppose_odds = ['2.5', '2.6', '2.7']
		o = {}

		if task_bl.is_able_to_create_new_task(outcome_id):
			# processing support side
			if len(arr_support_hs) == 0:
				hs = db.session.query(Handshake).filter(and_(Handshake.side==CONST.SIDE_TYPE['SUPPORT'], Handshake.outcome_id==outcome_id)).order_by(Handshake.date_created.desc()).first()
				result = True

				if hs is not None:
					n = time.mktime(datetime.now().timetuple())
					ds = time.mktime(utc_to_local(hs.date_created.timetuple())) 
					if n - ds <= 300: #5 minutes
						result = False
				if result:
					if hs is not None:
						odds = '{}'.format(hs.odds)
					else:
						odds = random.choice(support_odds)

					match = Match.find_match_by_id(outcome.match_id)
					o['odds'] = odds
					o['side'] = CONST.SIDE_TYPE['SUPPORT']
					o['outcome_id'] = outcome_id
					o['hid'] = outcome.hid
					o['match_date'] = match.date
					o['match_name'] = match.name
					o['outcome_name'] = outcome.name

					task = Task(
						task_type=CONST.TASK_TYPE['REAL_BET'],
						data=json.dumps(o),
						action=CONST.TASK_ACTION['INIT'],
						status=-1,
						contract_address=app.config['PREDICTION_SMART_CONTRACT'],
						contract_json=app.config['PREDICTION_JSON']
					)
					db.session.add(task)
					db.session.flush()

					print 'Add support odds --> {}'.format(task.to_json())
				

			# processing against side
			if len(arr_oppose_hs) == 0:
				hs = db.session.query(Handshake).filter(and_(Handshake.side==CONST.SIDE_TYPE['AGAINST'], Handshake.outcome_id==outcome_id)).order_by(Handshake.date_created.desc()).first()
				result = True

				if hs is not None:
					n = time.mktime(datetime.now().timetuple())
					ds = time.mktime(utc_to_local(hs.date_created.timetuple()))
					if n - ds <= 300: #5 minutes
						result = False
					
				if result:
					if hs is not None:
						odds = '{}'.format(hs.odds)
					else:
						odds = random.choice(oppose_odds)

					match = Match.find_match_by_id(outcome.match_id)
					o['odds'] = odds
					o['side'] = CONST.SIDE_TYPE['AGAINST']
					o['outcome_id'] = outcome_id
					o['hid'] = outcome.hid
					o['match_date'] = match.date
					o['match_name'] = match.name
					o['outcome_name'] = outcome.name

					task = Task(
						task_type=CONST.TASK_TYPE['REAL_BET'],
						data=json.dumps(o),
						action=CONST.TASK_ACTION['INIT'],
						status=-1,
						contract_address=app.config['PREDICTION_SMART_CONTRACT'],
						contract_json=app.config['PREDICTION_JSON']
					)
					db.session.add(task)
					db.session.flush()

					print 'Add against odds --> {}'.format(task.to_json())
		print '---------------------------------'
		db.session.commit()

	except Exception as e:
		db.session.rollback()
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("run_bots=>",exc_type, fname, exc_tb.tb_lineno)

@celery.task()
def send_mail(outcome_id, outcome_name):
	try:
		# Send mail to admin
		endpoint = '{}'.format(app.config['MAIL_SERVICE'])
		multipart_form_data = MultipartEncoder(
    		fields= {
				'body': 'Outcome name: {}. Outcome id: {}'.format(outcome_name, outcome_id),
				'subject': 'Dispute',
				'to[]': app.config['EMAIL'],
				'from': app.config['EMAIL']
			}
    	)
		res = requests.post(endpoint, data=multipart_form_data, headers={'Content-Type': multipart_form_data.content_type})

		if res.status_code > 400:
			print('Send mail is failed.')
		print 'Send mail result: {}'.format(res.json())

	except Exception as e:
		print("Send mail notification fail!")
		print e


@celery.task()
def update_contract_feed(arr_id, contract_address, contract_json):
	try:
		arr_handshakes = []
		for _id in arr_id:
			hs = {
				"id": CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(_id),
				"contract_address_s": {"set": contract_address},
				"contract_json_s": {"set": contract_json}
			}
			arr_handshakes.append(hs)

		endpoint = "{}/handshake/update".format(app.config['SOLR_SERVICE'])
		data = {
			# "add": arr_handshakes
			"update": arr_handshakes
		}
		res = requests.post(endpoint, json=data)
		if res.status_code > 400 or \
			res.content is None or \
			(isinstance(res.content, str) and 'null' in res.content):
			print "Update contract feeds fail"
			print res

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("add_feed=>",exc_type, fname, exc_tb.tb_lineno)
