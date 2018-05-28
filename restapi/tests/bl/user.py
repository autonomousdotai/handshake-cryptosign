#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from mock import patch
from tests.routes.base import BaseTestCase
from app import db, app
from app.models import User, Handshake
from app.bl.user import check_user_is_able_to_create_new_handshake
from app.helpers.message import MESSAGE

import mock
import json
import time

class TestUser(BaseTestCase):

    def send_email(fromEmail, toEmail, state=0):
        email = {
            "from": fromEmail,
            "to": toEmail,
            "subject": subject,
            "content": content
        }

        arr = app.config.get('email', [])
        arr.append(email)
        app.config['email'] = arr

    @mock.patch("app.routes.handshake.sg.send", side_effect=send_email)
    def test_check_user_is_able_to_create_new_handshake(self, mock_sg):
        Handshake.query.delete()
        response = self.register_user('trong1@autonomous.nyc', '1')
        data = json.loads(response.data.decode())
        token = data['data']['access_token']
        self.assertTrue(data['status'] == 1)
        self.assertEqual(response.status_code, 200)

        app.config['email'] = []

        params = {
            "value": 0,
            "term": 0,
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
        self.assertEqual(app.config['email'][0]['to'], 'trongdth@gmail.com')
        self.assertEqual(data['data']['industries_type'], 1)
        self.assertEqual(data['data']['from_email'], 'trong1@autonomous.nyc')
        self.assertEqual(data['data']['to_email'], 'trongdth@gmail.com')
        self.assertEqual(data['data']['source'], 'web')
        time.sleep(1)

        app.config['email'] = []
        params = {
            "value": 0.1,
            "term": 1,
            "to_address": "trongdth@gmail.com",
            "description": "1",
            "industries_type": 0
        }

        response = self.client.post(
                                'handshake/init',
                                data=params, 
                                headers={"Authorization": "Bearer {}".format(token)})

        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(app.config['email'][0]['to'], 'trongdth@gmail.com')
        self.assertEqual(data['data']['industries_type'], 0)
        self.assertEqual(data['data']['from_email'], 'trong1@autonomous.nyc')
        self.assertEqual(data['data']['to_email'], 'trongdth@gmail.com')
        self.assertEqual(data['data']['source'], 'web')
        time.sleep(1)
        app.config['email'] = []
        params = {
            "value": 0.2,
            "term": 1,
            "to_address": "trongdth@gmail.com",
            "description": "1",
            "industries_type": 0
        }

        response = self.client.post(
                                'handshake/init',
                                data=params, 
                                headers={"Authorization": "Bearer {}".format(token)})

        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(app.config['email'][0]['to'], 'trongdth@gmail.com')
        self.assertEqual(data['data']['industries_type'], 0)
        self.assertEqual(data['data']['from_email'], 'trong1@autonomous.nyc')
        self.assertEqual(data['data']['to_email'], 'trongdth@gmail.com')
        self.assertEqual(data['data']['source'], 'web')
        time.sleep(1)
        app.config['email'] = []
        params = {
            "value": 0.3,
            "term": 1,
            "to_address": "trongdth@gmail.com",
            "description": "1",
            "industries_type": 0
        }

        response = self.client.post(
                                'handshake/init',
                                data=params, 
                                headers={"Authorization": "Bearer {}".format(token)})

        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(app.config['email'][0]['to'], 'trongdth@gmail.com')
        self.assertEqual(data['data']['industries_type'], 0)
        self.assertEqual(data['data']['from_email'], 'trong1@autonomous.nyc')
        self.assertEqual(data['data']['to_email'], 'trongdth@gmail.com')
        self.assertEqual(data['data']['source'], 'web')
        time.sleep(1)
        app.config['email'] = []
        params = {
            "value": 0.4,
            "term": 1,
            "to_address": "trongdth@gmail.com",
            "description": "1",
            "industries_type": 0
        }
        
        response = self.client.post(
                                'handshake/init',
                                data=params, 
                                headers={"Authorization": "Bearer {}".format(token)})

        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(app.config['email'][0]['to'], 'trongdth@gmail.com')
        self.assertEqual(data['data']['industries_type'], 0)
        self.assertEqual(data['data']['from_email'], 'trong1@autonomous.nyc')
        self.assertEqual(data['data']['to_email'], 'trongdth@gmail.com')
        self.assertEqual(data['data']['source'], 'web')
        app.config['email'] = []
        time.sleep(1)
        params = {
            "value": 0.5,
            "term": 1,
            "to_address": "trongdth@gmail.com",
            "description": "1",
            "industries_type": 0
        }

        response = self.client.post(
                                'handshake/init',
                                data=params, 
                                headers={"Authorization": "Bearer {}".format(token)})

        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], MESSAGE.USER_NEED_PURCHASE_PRODUCT)
        

        user = User.find_user_with_email("trong1@autonomous.nyc")
        message = check_user_is_able_to_create_new_handshake(user)
        self.assertEqual(MESSAGE.USER_NEED_PURCHASE_PRODUCT, message)

        handshakes = db.session.query(Handshake).filter(Handshake.user_id==user.id).all()
        self.assertEqual(int(user.subscription_type), len(handshakes))


if __name__ == '__main__':
    unittest.main()