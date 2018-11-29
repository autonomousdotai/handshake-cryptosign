# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app.models import User, Handshake, Shaker, Outcome, Token, Referral
from app import db, app

import mock
import json
import time
import app.bl.referral as referral_bl

class TestReferralBluePrint(BaseTestCase):

    def clear_data_before_test(self):
        r = Referral.find_referral_by_uid(88)
        if r is not None:
            db.session.delete(r)
            db.session.commit()
        

    def test_check_user_join_referral_program(self):
        self.clear_data_before_test()
        code = 'A123'

        with self.client:
            Uid = 88
            response = self.client.get(
                                    '/referral/check',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)

            # generate referral code for user id 88
            r = Referral.find_referral_by_code(code)
            if r is not None:
                r.user_id = 88
            else:
                r = Referral(
                    code=code,
                    user_id=88
                )
                db.session.add(r)
            db.session.commit()

            # call again
            response = self.client.get(
                                    '/referral/check',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            self.assertEqual(data['data']['code'], code)

    
    def test_user_join_referral_program(self):
        self.clear_data_before_test()

        u = User.find_user_with_id(88)
        u.email = None
        db.session.commit()

        with self.client:
            Uid = 88
            response = self.client.get(
                                    '/referral/join',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)

            # user should have email address
            u.email = 'a@gmail.com'
            db.session.commit()

            # call again
            response = self.client.get(
                                    '/referral/join',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)


            # one more
            response = self.client.get(
                                    '/referral/join',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
    

if __name__ == '__main__':
    unittest.main()