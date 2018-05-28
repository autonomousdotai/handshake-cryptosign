#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from tests.routes.base import BaseTestCase
from mock import patch
from app import db, app
from app.models import Handshake, Device, User
from app.helpers.message import MESSAGE
from io import BytesIO

import os
import mock
import json
import time
import app.bl.handshake as handshake_bl

class TestHandshakeBluePrint(BaseTestCase):
    def send_email(fromEmail, toEmail, subject, content):
        email = {
            "from": fromEmail,
            "to": toEmail,
            "subject": subject,
            "content": content
        }

        arr = app.config.get('email', [])
        arr.append(email)
        app.config['email'] = arr

    def send_push(devices, title, body, data_message):
        push = {
            "devices": devices,
            "title": title,
            "body": body,
            "data_message": data_message
        }
        arr = app.config.get('push', [])
        arr.append(push)
        app.config['push'] = arr

    @mock.patch("app.routes.handshake.handshake_bl.sg.send", side_effect=send_email)
    @mock.patch("app.routes.handshake.handshake_bl.fcm.push_multi_devices", side_effect=send_push)
    def setUp(self, mock_fcm, mock_send_mail):
        with self.client:            
            response = self.register_user('trong2@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            token = data['data']['access_token']
            response = self.client.post(
                                'device/add',
                                data={"device_token": '456', "device_type": "ios"}, 
                                headers={"Authorization": "Bearer {}".format(token)})

            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            token = data['data']['access_token']
            response = self.client.post(
                                'device/add',
                                data={"device_token": '123', "device_type": "ios"}, 
                                headers={"Authorization": "Bearer {}".format(token)})

            if 'handshake_id' not in app.config or app.config['handshake_id'] is None:
                params = {
                    "value": 0,
                    "to_address": "trong2@autonomous.nyc",
                    "description": "contract exists",
                    "industries_type": 1
                }
                response = self.client.post(
                                        'handshake/init',
                                        data=params, 
                                        headers={"Authorization": "Bearer {}".format(token),
                                                "content_type": "multipart/form-data"})

                data = json.loads(response.data.decode())
                print data
                handshake_id = data['data']['id']
                
                app.config['handshake_id'] = handshake_id
                self.assertTrue(data['status'] == 1)
                self.assertEqual(response.status_code, 200)

    def tearDown(self):
        Device.query.delete()
        if len(db.session.query(Handshake).all()) >= 50:
            Handshake.query.delete()

    @mock.patch("app.routes.handshake.handshake_bl.sg.send", side_effect=send_email)
    @mock.patch("app.routes.handshake.handshake_bl.fcm.push_multi_devices", side_effect=send_push)
    def test_init_handshake(self, mock_fcm, mock_sg):
        """
        Test an user create handshake successfully through the api
        :scenerio:
        - payee init handshake to payer who not in handshake system
        expected:
        - handshake is created successfully
        - send email to payer + payee
        """
        with self.client:
            app.config['email'] = []
            app.config['push'] = []

            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            token = data['data']['access_token']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            
            params = {
                "value": 0,
                "to_address": "trongdth@gmail.com",
                "description": "test send email",
                "industries_type": 1
            }

            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token)})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(app.config['email']), 2) # send 2 emails
            self.assertEqual(data['data']['industries_type'], 1)
            self.assertEqual(data['data']['from_email'], 'trong1@autonomous.nyc')
            self.assertEqual(data['data']['to_email'], 'trongdth@gmail.com')
            self.assertEqual(data['data']['source'], 'web')
            
            app.config['email'] = []
            app.config['push'] = []

            params = {
                "value": 0.001,
                "to_address": "trongdth@gmail.com",
                "description": "test send email",
                "industries_type": 4
            }

            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token)})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(app.config['email']), 2) # send 2 emails
            self.assertEqual(data['data']['industries_type'], 4)
            self.assertEqual(data['data']['from_email'], 'trong1@autonomous.nyc')
            self.assertEqual(data['data']['to_email'], 'trongdth@gmail.com')
            self.assertEqual(data['data']['source'], 'web')


    @mock.patch("app.routes.handshake.handshake_bl.sg.send", side_effect=send_email)
    @mock.patch("app.routes.handshake.handshake_bl.fcm.push_multi_devices", side_effect=send_push)
    def test_init_handshake_with_email_and_wallet_address(self, mock_fcm, mock_sg):
        """
        :scenerio:
        - payee init handshake to payer (email, wallet address) who in handshake system
        expected:
        - handshake is created successfully
        - send email to payer
        """
        with self.client:
            app.config['email'] = []
            app.config['push'] = []

            response = self.register_user('trong2@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            wallet_address = data['data']['user']['wallet']['address']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            token = data['data']['access_token']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            
            params = {
                "value": 0,
                "to_address": "trong2@autonomous.nyc",
                "description": "test send email",
                "industries_type": 1
            }

            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token)})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(app.config['email']), 2)
            self.assertEqual(data['data']['industries_type'], 1)
            self.assertEqual(data['data']['from_email'], 'trong1@autonomous.nyc')
            self.assertEqual(data['data']['to_email'], 'trong2@autonomous.nyc')
            self.assertEqual(data['data']['source'], 'web')
            
            
            app.config['email'] = []
            app.config['push'] = []

            # test send wallet address

            params = {
                "value": 0.01,
                "to_address": wallet_address,
                "description": "test send email",
                "industries_type": 4
            }

            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token)})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(app.config['email']), 2)
            self.assertEqual(data['data']['industries_type'], 4)
            self.assertEqual(data['data']['from_email'], 'trong1@autonomous.nyc')
            self.assertEqual(data['data']['to_email'], 'trong2@autonomous.nyc')
            self.assertEqual(data['data']['source'], 'web')

    @mock.patch("app.routes.handshake.handshake_bl.sg.send", side_effect=send_email)
    @mock.patch("app.routes.handshake.handshake_bl.fcm.push_multi_devices", side_effect=send_push)
    def test_init_handshake_with_attachment(self, mock_fcm, mock_sg):
        """
        :scenerio:
        - payee init handshake with attachment to payer which in database
        :expected:
        - init handshake success
        - file upload successfully
        """
        with self.client:
            app.config['email'] = []
            app.config['push'] = []

            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            response = self.register_user('trong2@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            
            token = self.get_user_token()
            params = {
                "value": 0,
                "to_address": "trong2@autonomous.nyc",
                "description": "contract exists",
                "file": (BytesIO(b'example4'), 'example4.pdf'),
                "industries_type": 0,
                "source": "ios"
            }
            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token),
                                            "content_type": "multipart/form-data"})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 0)

            params = {
                "value": 0.1,
                "to_address": "trong2@autonomous.nyc",
                "description": "contract exists",
                "file": (BytesIO(b'example4'), 'example4.pdf'),
                "industries_type": 4,
                "source": "ios"
            }
            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token),
                                            "content_type": "multipart/form-data"})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['industries_type'], 4)
            time.sleep(10)
            self.assertEqual(data['data']['from_email'], 'trong1@autonomous.nyc')
            self.assertEqual(data['data']['to_email'], 'trong2@autonomous.nyc')
            self.assertEqual(data['data']['source'], 'ios')

    def test_view_handshake_with_valid_handshake_id(self):
        """
        :scenerio:
        - user call view handshake_id which in database
        :expected:
        - return contract file url
        """
        with self.client:
            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            token = data['data']['access_token']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            time.sleep(10)
            handshake_id = app.config['handshake_id']

            params = {
                "original": 1
            }

            response = self.client.post(
                                    "handshake/view_file/{}".format(handshake_id),
                                    data=params,
                                    headers={"Authorization": "Bearer {}".format(token)})

            with open("contract_file.pdf", 'wb+') as fd: 
                fd.write(response.data)

            handshake = db.session.query(Handshake).filter(Handshake.id==handshake_id).first()
            filename = "{}_decrypt.pdf".format(handshake.contract_file)
            original_path = "/Workspace/robotbase/cryptosign/restapi/app/files/pdf/{}".format(filename)

            self.assertIsNotNone(handshake)
            self.assertIsNotNone(handshake.contract_file)
            self.assertEqual(os.path.getsize("contract_file.pdf"), os.path.getsize(original_path))
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

    def test_view_handshake_with_invalid_handshake_id(self):
        """
        :scenerio:
        - user call view handshake_id which not in database
        :expected:
        - through error
        """
        with self.client:
            token = self.get_user_token()
            response = self.client.post(
                                    "handshake/view_file/{}".format(20000),
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)

    def test_init_handshake_failed_if_to_address_is_myself(self):
        """
        :scenerio:
        - user call init handshake with to_address is yourself (email, wallet_address)
        :expected:
        - through error
        """
        with self.client:
            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            wallet_address = data['data']['user']['wallet']['address']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(wallet_address)
            
            token = self.get_user_token()
            params = {
                "value": 0,
                "to_address": "trong1@autonomous.nyc",
                "description": "---",
                "industries_type": 1
            }
            
            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token)})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], MESSAGE.HANDSHAKE_CANNOT_SEND_TO_MYSELF)

            params = {
                "value": 0,
                "to_address": wallet_address,
                "description": "---",
                "industries_type": 2
            }
            
            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], MESSAGE.HANDSHAKE_CANNOT_SEND_TO_MYSELF)


            params = {
                "value": 0,
                "to_address": " Trong1@autonomous.nyc",
                "description": "---",
                "industries_type": 1
            }
            
            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], MESSAGE.HANDSHAKE_CANNOT_SEND_TO_MYSELF)

    @mock.patch("app.routes.handshake.handshake_bl.sg.send", side_effect=send_email)
    @mock.patch("app.routes.handshake.handshake_bl.fcm.push_multi_devices", side_effect=send_push)
    def test_init_handshake_will_fire_notification_to_address(self, mock_fcm, mock_sg):
        """
        :scenerio:
        - user call init handshake to address
        :expected:
        - fire notification to address
        """
        with self.client:
            app.config['email'] = []
            app.config['push'] = []

            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            # add device token for user 2
            response = self.register_user('trong2@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            user_id = data['data']['user']['id']
            dvs = Device.find_devices_with_user_id(user_id)
            for dv in dvs:
                db.session.delete(dv)
                db.session.commit()

            token = data['data']['access_token']
            response = self.client.post(
                                'device/add',
                                data={"device_token": '123', "device_type": "ios"}, 
                                headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            
            # call init handshake
            token = self.get_user_token()
            params = {
                "value": 0,
                "to_address": "trong2@autonomous.nyc",
                "description": "--- playing football ---",
                "industries_type": 1
            }
            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token),
                                            "content_type": "multipart/form-data"})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['industries_type'], 1)
            
            time.sleep(2)
            devices = app.config['push']
            self.assertEqual(len(devices), 1)
            self.assertTrue('123' in app.config['push'][0]['devices'])

    def test_init_handshake_failed_value(self):
        """
        :scenerio:
        - payee init payable / basic handshake with wrong value
        :expected:
        - return error
        """
        with self.client:
            app.config['email'] = []
            app.config['push'] = []

            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            token = data['data']['access_token']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            params = {
                "value": -0.1,
                "to_address": "trong2@autonomous.nyc",
                "description": "contract exists",
                "industries_type": 4
            }
            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token),
                                            "content_type": "multipart/form-data"})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], MESSAGE.HANDSHAKE_VALUE_GREATER_THAN_0)


            params = {
                "value": -0.1,
                "to_address": "trong2@autonomous.nyc",
                "description": "contract exists",
                "industries_type": 4
            }
            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token),
                                            "content_type": "multipart/form-data"})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], MESSAGE.HANDSHAKE_VALUE_GREATER_THAN_0)


            params = {
                "value": 0,
                "to_address": "trong2@autonomous.nyc",
                "description": "contract exists",
                "industries_type": 4
            }
            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token),
                                            "content_type": "multipart/form-data"})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], MESSAGE.HANDSHAKE_TERM_AND_VALUE_NOT_MATCH)


            params = {
                "value": "a",
                "to_address": "trong2@autonomous.nyc",
                "description": "contract exists",
                "industries_type": 4
            }
            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token),
                                            "content_type": "multipart/form-data"})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], MESSAGE.HANDSHAKE_AMOUNT_INVALID)

    @mock.patch("app.routes.handshake.handshake_bl.sg.send", side_effect=send_email)
    @mock.patch("app.routes.handshake.handshake_bl.fcm.push_multi_devices", side_effect=send_push)
    def test_shake_handshake(self, mock_fcm, mock_send_mail):
        with self.client:
            app.config['email'] = []
            app.config['push'] = []

            handshake_id = app.config['handshake_id']
            response = self.register_user('trong2@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            token = data['data']['access_token']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            params = {
                "handshake_id": handshake_id
            }
            response = self.client.post(
                                    'handshake/shake',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token)})

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            

    @mock.patch("app.routes.handshake.handshake_bl.sg.send", side_effect=send_email)
    @mock.patch("app.routes.handshake.handshake_bl.fcm.push_multi_devices", side_effect=send_push)
    def test_verify_signed_handshake(self, mock_fcm, mock_send_mail):
        with self.client:
            time.sleep(35)
            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            token = data['data']['access_token']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            handshake_id = app.config['handshake_id']
            handshake = db.session.query(Handshake).filter(Handshake.id==handshake_id).first()

            response = self.client.get(
                                    "handshake/{}".format(handshake_id),
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(data['data']['signed_contract_file'])

            response = self.client.post(
                                    "handshake/view_file/{}".format(handshake_id),
                                    headers={"Authorization": "Bearer {}".format(token)})

            with open("signed_contract_file.pdf", 'wb+') as fd: 
                fd.write(response.data)

            filename = "{}_decrypt.pdf".format(handshake.signed_contract_file)
            original_path = "/Workspace/robotbase/cryptosign/restapi/app/files/pdf/{}".format(filename)
            self.assertEqual(os.path.getsize("signed_contract_file.pdf"), os.path.getsize(original_path))
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)


    def test_get_industries(self):
        with self.client:
            token = self.get_user_token()
            response = self.client.get(
                                    "handshake/industries",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']), 11)
            self.assertEqual(data['data'][0]['name'], 'Promise')
            self.assertEqual(data['data'][1]['name'], u'It\u2019s a date - don\u2019t be late')
            self.assertEqual(data['data'][2]['name'], 'IOU')
            self.assertEqual(data['data'][3]['name'], 'Invoice')
            self.assertEqual(data['data'][4]['name'], 'Get healthy')
            self.assertEqual(data['data'][5]['name'], 'Kick a habit')
            self.assertEqual(data['data'][6]['name'], 'A good cause')
            self.assertEqual(data['data'][7]['name'], 'Reading challenge')
            self.assertEqual(data['data'][8]['name'], 'A friend in need')
            
            self.assertEqual(data['data'][8]['name'], 'Invest')
            self.assertEqual(data['data'][9]['name'], 'Job Offer')
            self.assertEqual(data['data'][10]['name'], 'Sign PDF contract ')
            self.assertEqual(data['data'][11]['name'], 'Create your own')


    def test_message_for_industries_type(self):
        with self.client:
            token = self.get_user_token()
            response = self.client.get(
                                    "handshake/message/0",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 0)
            self.assertEqual(data['data']['message'], "")

            response = self.client.get(
                                    "handshake/message/2",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 2)
            self.assertEqual(data['data']['message'], "I've got a date on the blockchain.\nMake yours here.")

            response = self.client.get(
                                    "handshake/message/20",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 20)
            self.assertEqual(data['data']['message'], "")

            response = self.client.get(
                                    "handshake/message/3",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 3)
            self.assertEqual(data['data']['message'], "The blockchain forgets no IOUs.\nImmortalize yours.")

            response = self.client.get(
                                    "handshake/message/4",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 4)
            self.assertEqual(data['data']['message'], "Please find attached this invoice on the blockchain.\nPut yours in code.")

            response = self.client.get(
                                    "handshake/message/5",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 5)
            self.assertEqual(data['data']['message'], "We shook on it.\nSeal the deal on the blockchain.")

            response = self.client.get(
                                    "handshake/message/6",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 6)
            self.assertEqual(data['data']['message'], "We're working together!\nPut that job offer in code.")

            response = self.client.get(
                                    "handshake/message/7",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 7)
            self.assertEqual(data['data']['message'], "I made a promise on the blockchain.\nMake yours here.")

            response = self.client.get(
                                    "handshake/message/8",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 8)
            self.assertEqual(data['data']['message'], "Getting healthy on the blockchain.\nStart here.")

            response = self.client.get(
                                    "handshake/message/9",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 9)
            self.assertEqual(data['data']['message'], "This is how to use the blockchain to kick a habit.\nStart here.")

            response = self.client.get(
                                    "handshake/message/10",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 10)
            self.assertEqual(data['data']['message'], "We're doing our part. It's on record!\nMake a difference on the blockchain.")

            response = self.client.get(
                                    "handshake/message/11",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 11)
            self.assertEqual(data['data']['message'], "Getting smarter with Handshake.\nPut your reading list on the blockchain.")

            response = self.client.get(
                                    "handshake/message/12",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 12)
            self.assertEqual(data['data']['message'], "Smart contractually obliged to be a good friend.\nShake hands here.")

            response = self.client.get(
                                    "handshake/message/13",
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['id'], 13)
            self.assertEqual(data['data']['message'], "I crypto-signed a document. Move over e-signatures!\nSign yours here with Handshake.")
    
if __name__ == '__main__':
    unittest.main()