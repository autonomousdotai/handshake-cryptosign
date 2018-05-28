from tests.routes.base import BaseTestCase
from mock import patch
from app.models import Device, Wallet
from app import db
from app.helpers.message import MESSAGE

import mock
import json
import time
import app.bl.user as user_bl

class TestDeviceBluePrint(BaseTestCase):

    def setUp(self):
        Device.query.delete()

    def test_add_device_token(self):
        """
        Test add a device token
        :return:
        """
        with self.client:
            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            user_id = data['data']['user']['id']
            token = data['data']['access_token']

            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            response = self.client.post(
                                'device/add',
                                data={"device_token": '123', "device_type": "ios"}, 
                                headers={"Authorization": "Bearer {}".format(token)})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['device_token'], '123')
            devices = Device.find_devices_with_user_id(user_id)
            self.assertEqual(len(devices), 1)

            device_list = data['data']
            self.assertGreater(len(device_list), 1)

            # add this device token again
            response = self.client.post(
                                'device/add',
                                data={"device_token": '123', "device_type": "ios"}, 
                                headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            device = Device.find_devices_with_user_id(user_id)
            self.assertGreater(len(device_list), 1)

    def test_remove_device_token(self):
        """
        Test remove a device token
        :return:
        """
        with self.client:
            token = self.get_user_token()
            response = self.client.post(
                                'device/add',
                                data={"device_token": '123', "device_type": "ios"}, 
                                headers={"Authorization": "Bearer {}".format(token)})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            response = self.client.post(
                                'device/remove',
                                data={"device_token": "123"}, 
                                headers={"Authorization": "Bearer {}".format(token)})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)        

    
if __name__ == '__main__':
    unittest.main()