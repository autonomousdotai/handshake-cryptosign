from tests.routes.base import BaseTestCase
from mock import patch
from app.models import Device, Tx, Handshake
from app import db, app
from app.helpers.message import MESSAGE
from app.constants import Handshake as HandshakeStatus

import mock
import json
import time
import app.bl.user as user_bl

class TestEventBluePrint(BaseTestCase):

    def send_push(devices, title, body, data_message):
        app.config['devices'] = devices
        app.config['title'] = title
        app.config['body'] = body
        app.config['data_message'] = data_message

    @mock.patch("app.routes.handshake.handshake_bl.fcm.push_multi_devices", side_effect=send_push)
    def setUp(self, mock_fcm):
        with self.client:
            Handshake.query.delete()
            Device.query.delete()

            response = self.register_user('trong2@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            token = data['data']['access_token']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            response = self.client.post(
                                'device/add',
                                data={"device_token": '456', "device_type": "ios"}, 
                                headers={"Authorization": "Bearer {}".format(token)})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)


            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
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

            params = {
                "value": 0,
                "term": 0,
                "to_address": "trong2@autonomous.nyc",
                "description": "contract exists",
                "industries_type": 0
            }
            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            time.sleep(4)
            handshake_id = data['data']['id']
            app.config['handshake_id'] = handshake_id

    @mock.patch("app.routes.handshake.handshake_bl.fcm.push_multi_devices", side_effect=send_push)
    def test_event_for_init_handshake(self, mock_fcm):
        """
        :scenerio: 
        - registry user A
        - A init handshake to user B
        - Call event to update init handshake
        :expected:
        - status is updated successfully
        """
        with self.client:
            response = self.register_user('trong2@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            user_id = data['data']['user']['id']
            txs = Tx.query.filter_by(scope_id=app.config['handshake_id']).all()
            self.assertIsNotNone(txs)
            self.assertEqual(len(txs), 1)
            
            tx_id = txs[0].id
            # call event to update this handshake

            params = {
                "txId": str(tx_id),
                "txStatus": 1,
                "blockTimeStamp": "1521781332000",
                "blockNumber": 10,
                "events": {
                    "BasicHandshake.__init": {
                        "hid": "200",
                        "offchain": "cts_{}".format(app.config['handshake_id'])
                    }
                }
            }
            
            response = self.client.post(
                                    'event',
                                    data=json.dumps(params),
                                    headers={'Content-type': 'application/json'})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            time.sleep(2)

            handshake = Handshake.query.filter(Handshake.hid==200).first()
            data_message = app.config['data_message']            

            self.assertIsNotNone(handshake)
            self.assertEqual(handshake.id, data_message['data']['id'])
            self.assertEqual(handshake.status, HandshakeStatus['STATUS_INITED'])
            self.assertEqual(handshake.bk_status, HandshakeStatus['STATUS_INITED'])

            devices = app.config['devices']
            uDevice = db.session.query(Device.device_token).filter(Device.user_id==user_id).first()
            self.assertGreaterEqual(len(devices), 2)
            if uDevice[0] not in devices:
                self.assertTrue(False)
    
if __name__ == '__main__':
    unittest.main()