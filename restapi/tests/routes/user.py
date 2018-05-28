# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app.models.user import User, Handshake
import app.bl.user as user_bl
from app import db, app
from app.helpers.message import MESSAGE

import mock
import json
import time

class TestUserBluePrint(BaseTestCase):

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

    def test_user_registration(self):
        """
        Test a user is successfully created through the api
        :return:
        """
        with self.client:
            user = User.query.filter_by(email='trong101@autonomous.nyc').first()
            if user is not None:
                db.session.delete(user)

            response = self.register_user('trong101@autonomous.nyc', '123456', '')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['user']['email'], 'trong101@autonomous.nyc')
            self.assertEqual(data['data']['user']['name'], '')
            self.assertIsNotNone(data['data']['user']['wallet']['address'])

            user = User.find_user_with_email('trong101@autonomous.nyc')
            self.assertIsNotNone(user)

            response = self.register_user('trong101@autonomous.nyc', '123456', '123')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['user']['email'], 'trong101@autonomous.nyc')
            self.assertEqual(data['data']['user']['name'], '123')
            self.assertIsNotNone(data['data']['user']['wallet']['address'])

            response = self.register_user('trong101@autonomous.nyc', '123456', '456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['data']['user']['email'], 'trong101@autonomous.nyc')
            self.assertEqual(data['data']['user']['name'], '456')
            self.assertIsNotNone(data['data']['user']['wallet']['address'])
            
    def test_user_registration_with_capitalized_email_still_success(self):
        with self.client:
            response = self.register_user('TRONG1@autonomous.nyc', '123456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

    def test_user_registration_with_wrong_email(self):
        with self.client:
            response = self.register_user('trong1', '123456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], MESSAGE.USER_INVALID_EMAIL)

    @mock.patch("app.routes.user.user_bl.autonomous_auth_user")
    @mock.patch("app.routes.user.user_bl.autonomous_sign_in")
    def test_user_registration_with_autonomous_auth_user_and_autonomous_sign_in_response_error(self, mock_autonomous_sign_in, mock_autonomous_auth_user):
        with self.client:
            # fake this user not in autonomous system
            response = {
                "status": -1,
                "message": "WTF"
            }
            mock_autonomous_auth_user.return_value = response
            # fake sign-in this user successfully
            mock_autonomous_sign_in.return_value = response

            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())

            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], "WTF")


    @mock.patch("app.routes.user.user_bl.autonomous_auth_user")
    @mock.patch("app.routes.user.user_bl.autonomous_sign_in")
    def test_user_registration_with_autonomous_auth_user_response_error(self, mock_autonomous_sign_in, mock_autonomous_auth_user):
        with self.client:
            # fake this user not in autonomous system
            response = {
                "status": -1,
                "message": "WTF"
            }
            mock_autonomous_auth_user.return_value = response

            # fake sign-in this user successfully
            response = {
                "status": 1,
                "customer": {
                    "city": "",
                    "code": "3594e6",
                    "country": "",
                    "state_region": "",
                    "id": 79406,
                    "credit": 0,
                    "eth_private_key": "U2FsdGVkX18tsYAuz4uFmJurdgP9kRZRrswtTXupgwDRn9HVxx85hFABpZGdnHi3Wo5vAiTzO8L1jtNGJ0rN9j1CU0ebIAnRPeBUumiA04KnxxiegkCqGfUrUmxV4w/0",
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRyb25nMTAxQGF1dG9ub21vdXMubnljIiwiZXhwIjoxNTI0MDQyMjQxLCJpZCI6Nzk0MDZ9.q_dApzHAaXYKhceZ73tdYx8Bt1iuVzdQ-vsq-UQi13s",
                    "address": "",
                    "fullname": "",
                    "eth_balance": 0,
                    "type": 2,
                    "email": "trong101@autonomous.nyc",
                    "eth_address": "0x906fBb4b60cd70BF3C9Eec4b883D6C9AC5DCCC63"
                },
                "message": ""
            }
            mock_autonomous_sign_in.return_value = response

            response = self.register_user('trong101@autonomous.nyc', '123456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertNotEqual("0x906fBb4b60cd70BF3C9Eec4b883D6C9AC5DCCC63", data['data']['user']['wallet']['address'])
            self.assertEqual(response.status_code, 200)

            cdata = data["data"]
            self.assertIsNotNone(cdata['access_token'])
            self.assertIsNotNone(cdata['user']['email'])
            self.assertEqual(cdata['user']['email'], 'trong101@autonomous.nyc')


    def test_user_auth(self):
        """
        Test a user is successfully verified through the web
        :return:
        """
        with self.client:
            response = self.auth_user('trong1@autonomous.nyc', 79335, '')
            data = json.loads(response.data.decode())
            print data
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

    def test_user_auth_with_wrong_id(self):
        with self.client:
            response = self.auth_user('trong1@autonomous.nyc', 7933511, '')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], MESSAGE.USER_INVALID_INPUT)

    @mock.patch("app.routes.user.user_bl.autonomous_verify_email")
    def test_user_auth_with_autonomous_verify_email_function_response_error(self, mock_autonomous_verify_email):
        with self.client:
            response = {
                "status": -1,
                "message": "WTF"
            }
            mock_autonomous_verify_email.return_value = response
            response = self.auth_user("trong1@autonomous.nyc", 79335, '')
            data = json.loads(response.data.decode())

            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], MESSAGE.USER_INVALID_INPUT)

    @mock.patch("app.routes.handshake.handshake_bl.sg.send", side_effect=send_email)
    def test_user_registration_will_update_to_address_field_in_tx_table(self, mock_sg):
        with self.client:
            # remove payer user first
            user = User.find_user_with_email("trongdth@autonomous.nyc")
            if user is not None:
                db.session.delete(user)
                db.session.commit()            

            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            
            # init handshake
            token = self.get_user_token()
            params = {
                "value": 0,
                "term": 0,
                "to_address": "trongdth@autonomous.nyc",
                "description": "--",
                "industries_type": 4
            }

            response = self.client.post(
                                    'handshake/init',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token)})

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            handshakes = Handshake.query.filter(Handshake.to_address=='trongdth@autonomous.nyc').all()
            self.assertGreater(len(handshakes), 0)

            # registry with trongdth@autonomous.nyc
            response = self.register_user('trongdth@autonomous.nyc', '123456')            
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            handshakes = Handshake.query.filter(Handshake.to_address=='trongdth@autonomous.nyc').all()
            self.assertEqual(len(handshakes), 0)

    def test_update_user_profile(self):
        with self.client:
            token = self.get_user_token()
            params = {
                "name": 'test'
            }

            response = self.client.post(
                                    'update-profile',
                                    data=params, 
                                    headers={"Authorization": "Bearer {}".format(token)})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            response = self.auth_user('trong1@autonomous.nyc', 1, '')
            data = json.loads(response.data.decode())

            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            
            user = data['data']['user']
            self.assertEqual(user['name'], 'test')
            


    
if __name__ == '__main__':
    unittest.main()