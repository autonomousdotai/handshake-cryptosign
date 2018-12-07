# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app.models import User, Handshake, Shaker, Outcome, Token, Referral
from app import db, app
from sqlalchemy import bindparam, literal_column, func
from app.helpers.message import MESSAGE
from app.constants import Handshake as HandshakeStatus

import mock
import json
import time
import app.bl.user as user_bl

class TestUserBluePrint(BaseTestCase):

    def clear_data_before_test(self):
        token1 = Token.find_token_by_id(1)
        token1.tid = None
        token1.status = -1

        token2 = Token.find_token_by_id(2)
        token2.tid = None
        token2.status = -1

        # reset users
        users = db.session.query(User).filter(User.email=='trongdth@gmail.com').all()
        for u in users:
            u.email = None

        # reset referral code
        referral = db.session.query(Referral).filter(Referral.user_id==66).first()
        if referral is not None:
            db.session.delete(referral)

        user = User.find_user_with_id(66)
        user.tokens = []

        db.session.flush()
        db.session.commit()
        

    def test_user_approve_token(self):
        self.clear_data_before_test()

        with self.client:
            Uid = 66
            params = {
                "token_id": 1
            }
            response = self.client.post(
                                    '/approve_token',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)

            # approve token first
            token = Token.find_token_by_id(1)
            token.tid = 0
            token.status = 1

            # call appprove token again
            response = self.client.post(
                                    '/approve_token',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

    
    def test_user_subscribe_email_without_referral_code(self):
        self.clear_data_before_test()

        with self.client:
            Uid = 66
            params = {
                "email": "trongdth@gmail.com"
            }
            response = self.client.post(
                                    '/subscribe',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            # call subscribe again
            response = self.client.post(
                                    '/subscribe',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)


    def test_user_subscribe_email_with_referral_code(self):
        self.clear_data_before_test()

        # claim referral code to uid 88
        code = '1ABC'
        r = Referral.find_referral_by_code(code)
        if r is None:
            r = Referral(
                code=code,
                user_id=88
            )
            db.session.add(r)
        else:
            r.user_id = 88
        db.session.commit()


        with self.client:
            Uid = 66
            params = {
                "email": "trongdth@gmail.com",
                "referral_code": code
            }
            response = self.client.post(
                                    '/subscribe',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            user = User.find_user_with_id(66)
            self.assertEqual(user.invited_by_user, 88)


    def test_subscribe_notification(self):
        self.clear_data_before_test()

        # clear email
        users = db.session.query(User).filter(User.email=='a123a@gmail.com').all()
        for u in users:
            u.email = None
            db.session.flush()

        db.session.commit()

        with self.client:
            Uid = 66
            params = {
                "email": "a123a@gmail.com"
            }
            response = self.client.post(
                                    '/subscribe-notification',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            user = User.find_user_with_id(66)
            self.assertEqual(user.email, 'a123a@gmail.com') 

            # call again
            params = {
                "email": "a123a@gmail.com"
            }
            response = self.client.post(
                                    '/subscribe-notification',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
    

    def test_subscribe_notification_with_user_not_verified(self):
        self.clear_data_before_test()

        # clear email
        users = db.session.query(User).filter(User.email=='a123a@gmail.com').all()
        for u in users:
            u.email = None
            db.session.flush()

        db.session.commit()

        with self.client:
            Uid = 66
            params = {
                "email": "a123a@gmail.com",
                "need_send_verification_code": 1
            }
            response = self.client.post(
                                    '/subscribe-notification',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)

            # set email to user first
            u = User.find_user_with_id(66)
            u.email = 'a123a@gmail.com'
            db.session.commit()

            # call again
            params = {
                "email": "a123a@gmail.com",
                "need_send_verification_code": 1
            }
            response = self.client.post(
                                    '/subscribe-notification',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)


    def test_subscribe_notification_with_user_not_verified(self):
        self.clear_data_before_test()

        with self.client:
            Uid = 66
            params = {
                "ids": [9998, 9999],
            }
            response = self.client.post(
                                    '/user/habit',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

if __name__ == '__main__':
    unittest.main()