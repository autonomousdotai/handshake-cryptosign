from tests.routes.base import BaseTestCase
from mock import patch
from app import db
from app.models import Match, Outcome
from app.helpers.message import MESSAGE

import mock
import json
import time
import app.bl.user as user_bl

class TestOutcomeBluePrint(BaseTestCase):

	def setUp(self):
		# create match
		match = Match.find_match_by_id(1)
		if match is None:
			match = Match(
				id=1
			)
			db.session.add(match)
			db.session.commit()

		# create outcome
		outcome = Outcome.find_outcome_by_id(88)
		if outcome is None:
			outcome = Outcome(
				id=88,
				match_id=1,
				name="1",
				hid=88,
				public=0,
				created_user_id=66
			)
			db.session.add(outcome)
			db.session.commit()

		else:
			outcome.public = 0
			outcome.name = "1"
			outcome.created_user_id = 66
			db.session.commit()


	def clear_data_before_test(self):
		pass

	def test_add_outcome(self):
		with self.client:
			pass

	def test_remove_outcome(self):
		with self.client:
			pass

	def test_generate_link(self):
		with self.client:

			params = {
				"outcome_id": 88
			}
			Uid = 66			
			response = self.client.post(
									'/outcome/generate-link',
									data=json.dumps(params), 
									content_type='application/json',
									headers={
										"Uid": "{}".format(Uid),
										"Fcm-Token": "{}".format(123),
										"Payload": "{}".format(123),
									})

			data = json.loads(response.data.decode()) 
			data_json = data['data']
			self.assertTrue(data['status'] == 1)

			actual = data_json['slug_short']
			expected = '?match=1&outcome=88&ref=66&is_private=1'
			self.assertEqual(actual, expected)
	

if __name__ == '__main__':
	unittest.main()