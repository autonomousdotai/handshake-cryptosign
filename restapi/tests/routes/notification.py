from tests.routes.base import BaseTestCase
from mock import patch
from app import db
from app.helpers.message import MESSAGE
from app.models import Notification
from app.helpers.utils import local_to_utc, parse_date_string_to_timestamp
from datetime import datetime, timedelta

import mock
import json
import time
import app.constants as CONST

class TestNotifBluePrint(BaseTestCase):

	def setUp(self):
		# create notif
		pass

	def clear_data_before_test(self):
		notif = Notification.find_notif_by_id(2)
		if notif is None:
			notif = Notification(
				id=2,
				name='Notification active',
				start_time=datetime.utcnow()+ timedelta(days=1),
				expire_time=datetime.utcnow()+ timedelta(days=2),
				data = '{"a":1}',
				type = CONST.COMMUNITY_TYPE['PUBLIC'],
				status = CONST.NOTIF_STATUS['ACTIVE']
			)
			db.session.add(notif)
		else:
			notif.start_time=datetime.utcnow()+ timedelta(days=1)
			notif.expire_time=datetime.utcnow()+ timedelta(days=2)

		db.session.commit()

		notif = Notification.find_notif_by_id(4)
		if notif is None:
			notif = Notification(
				id=4,
				name='Notification private',
				start_time=datetime.utcnow()+ timedelta(days=1),
				expire_time=datetime.utcnow()+ timedelta(days=2),
				data = '{"a":1}',
				type = CONST.COMMUNITY_TYPE['PRIVATE'],
				status = CONST.NOTIF_STATUS['INACTIVE']
			)
			db.session.add(notif)
		else:
			notif.tart_time=datetime.utcnow()+ timedelta(days=1)
			notif.expire_time=datetime.utcnow()+ timedelta(days=2)
		db.session.commit()

		notif = Notification.find_notif_by_id(5)

		if notif is None:
			notif = Notification(
				id=5,
				name='Notification expired',
				start_time=datetime.utcnow() - timedelta(days=2),
				expire_time=datetime.utcnow() - timedelta(days=1),
				data = '{"a":1}',
				type = CONST.COMMUNITY_TYPE['PUBLIC'],
				status = CONST.NOTIF_STATUS['ACTIVE']
			)
			db.session.add(notif)
		else:
			notif.tart_time=datetime.utcnow() - timedelta(days=2)
			notif.expire_time=datetime.utcnow() - timedelta(days=1)

		db.session.commit()

	def test_get_notifs_active(self):
		self.clear_data_before_test()
		arr_hs = []
		# ----- 
		with self.client:
			Uid = 66

			response = self.client.get(
									'/notif',
									headers={
										"Uid": "{}".format(Uid),
										"Fcm-Token": "{}".format(123),
										"Payload": "{}".format(123),
									})

			data = json.loads(response.data.decode())
			self.assertTrue(data['status'] == 1)

			data_json = data['data']
			self.assertTrue(data['status'] == 1)
			for item in data_json:
				if item['expire_time'] < local_to_utc(datetime.now().timetuple()):
					return False

	def test_post_newnotif(self):
		self.clear_data_before_test()
		# ----- 
		with self.client:
			Uid = 66
			params = [{
				"name": "Notification private",
				"start_time": local_to_utc((datetime.utcnow()+ timedelta(days=1)).timetuple()),
				"expire_time": local_to_utc((datetime.utcnow()+ timedelta(days=2)).timetuple()),
				"data": "{\"a\":1}",
				"type": "{}".format(CONST.COMMUNITY_TYPE['PUBLIC']),
				"status": "{}".format(CONST.NOTIF_STATUS['ACTIVE'])
			}]

			response = self.client.post(
									'/notif/add',
									data=json.dumps(params), 
									content_type='application/json',
									headers={
										"Uid": "{}".format(Uid),
										"Fcm-Token": "{}".format(123),
										"Payload": "{}".format(123),
									})
			data = json.loads(response.data.decode())
			self.assertTrue(data['status'] == 1)
			data_json = data['data']
			self.assertTrue(data['status'] == 1)

	def test_edit_notif(self):
		self.clear_data_before_test()
		# ----- 
		with self.client:
			Uid = 66
			start_time = local_to_utc((datetime.utcnow() - timedelta(days=1)).timetuple())
			expire_time = local_to_utc((datetime.utcnow() - timedelta(days=2)).timetuple())
			params = {
				"name": "Notification private edit",
				"start_time": start_time,
				"expire_time": expire_time
			}

			response = self.client.put(
									'/notif/edit/2',
									data=json.dumps(params), 
									content_type='application/json',
									headers={
										"Uid": "{}".format(Uid),
										"Fcm-Token": "{}".format(123),
										"Payload": "{}".format(123),
									})
			data = json.loads(response.data.decode())
			self.assertTrue(data['status'] == 1)
			data_json = data['data']
			self.assertTrue(data_json['name'] == "Notification private edit")
			self.assertTrue(data_json['start_time'] == start_time)
			self.assertTrue(data_json['expire_time'] == expire_time)

	def test_delete_notif(self):
		self.clear_data_before_test()
		# ----- 
		with self.client:
			Uid = 66
			params = {}

			response = self.client.delete(
									'/notif/remove/2',
									data=json.dumps(params), 
									content_type='application/json',
									headers={
										"Uid": "{}".format(Uid),
										"Fcm-Token": "{}".format(123),
										"Payload": "{}".format(123),
									})
			data = json.loads(response.data.decode())
			notif = Notification.find_notif_by_id(2)
			self.assertTrue(data['status'] == 1)
			self.assertTrue(notif == None)

if __name__ == '__main__':
	unittest.main()