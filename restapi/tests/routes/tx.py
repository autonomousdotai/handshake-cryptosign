from tests.routes.base import BaseTestCase
from mock import patch
from app.models import Device, Wallet
from app import db
from app.helpers.message import MESSAGE

import mock
import json
import time
import app.bl.user as user_bl

class TestTransactionBluePrint(BaseTestCase):

    def test_list_of_transaction(self):
        """
        Test get all list transaction
        :return:
        """
        with self.client:
            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            user_id = data['data']['user']['id']
            token = data['data']['access_token']

            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            response = self.client.get(
                                    'tx/1',
                                    headers={"Authorization": "Bearer {}".format(token)})

            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

    def test_list_of_transaction(self):
        """
        Test get all list transaction
        :return:
        """
        with self.client:
            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            user_id = data['data']['user']['id']
            token = data['data']['access_token']

            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            response = self.client.get(
                                    'tx/1',
                                    headers={"Authorization": "Bearer {}".format(token)})

            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
    
if __name__ == '__main__':
    unittest.main()