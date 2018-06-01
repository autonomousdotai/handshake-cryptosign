#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from mock import patch
from datetime import datetime
from app import db, app
from app.models import Handshake, User

import app.bl.handshake as handshake_bl
import app.constants as CONST
import mock
import json


class TestHandshakeBl(BaseTestCase):

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


    def setUp(self):
        with self.client:
            response = self.register_user('trong1@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            app.config['from_address'] = data['data']['user']['wallet']['address']
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


            response = self.register_user('trong2@autonomous.nyc', '1')
            data = json.loads(response.data.decode())
            app.config['to_address'] = data['data']['user']['wallet']['address']
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


    def test_is_need_send_notification(self):
        handshake = Handshake.query.first()
        expected = True
        actual = handshake_bl.is_need_fire_notification_for_handshake(handshake)
        self.assertEqual(actual, expected)

        handshake = Handshake(
			value=0,
			term=0,
			from_address='',
			to_address='',
            escrow_date=datetime.now(),
            delivery_date=datetime.now(),
			from_email='trong1@autonomous.nyc',
			to_email='trong2@autonomous.nyc',
			description='hello',
			user_id='1',
			industries_type=0,
			source='web',
		)
        handshake.date_created = datetime.now()
        expected = False
        actual = handshake_bl.is_need_fire_notification_for_handshake(handshake)
        self.assertEqual(actual, expected)
        

    @mock.patch("app.bl.handshake.sg.send", side_effect=send_email)
    @mock.patch("app.bl.handshake.fcm.push_multi_devices", side_effect=send_push)
    def test_send_notification(self, mock_fcm, mock_sg):
        """
        test case 1:
            scenerio:
                + user (trong1@autonomous.nyc) init handshake to trong2@autonomous.nyc from web or mobile
            expected:
                + trong1@autonomous.nyc will receive an email (just init handshake)
                + trong2@autonomous.nyc will receive an email (trong1 just sent a handshake)
        """
        app.config['email'] = []
        app.config['push'] = []
        handshake = Handshake(
			value=0,
			term=0,
			from_address=app.config['from_address'],
			to_address=app.config['to_address'],
            escrow_date=datetime.now(),
            delivery_date=datetime.now(),
			from_email='trong1@autonomous.nyc',
			to_email='trong2@autonomous.nyc',
			description='hello',
			user_id='1',
			industries_type=0,
			source='web',
		)
        handshake_bl.send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['INIT'], source='web')
        
        arr = app.config['email']
        self.assertEqual(2, len(arr))

        payer = arr[0]
        payee = arr[1]

        print payer
        self.assertEqual(payer['content'], "<html><head><title>Handshake</title></head><body>trong1@autonomous.nyc needs your cryptographic signature on an agreement!. <br><br>Visit <a href='https://www.autonomous.ai/handshake>www.autonomous.ai/handshake</a> to add your blockchain-protected mark <br><br> Or download Handshake for mobile on <a href='https://itunes.apple.com/us/app/crypto-handshake/id1360132818?ls=1&mt=8'>iOS</a> or <a href='https://play.google.com/store/apps/details?id=com.mobile_handshake'>Google play</a> </body></html>")
        self.assertEqual(payer['from'], "trong1@autonomous.nyc")
        self.assertEqual(payer['to'], "trong2@autonomous.nyc")
        self.assertEqual(payer['subject'], "trong1@autonomous.nyc wants to Handshake with you!")
        print "---------\n"
        print payee
        self.assertEqual(payee['content'], "<html><head><title>Handshake</title></head><body>Your Handshake is being processed on the blockchain! We will send you a status update once it has been successfully initiated. <br><br> Handshake Team </body></html>")
        self.assertEqual(payee['from'], "handshake@autonomous.nyc")
        self.assertEqual(payee['to'], "trong1@autonomous.nyc")
        self.assertEqual(payee['subject'], "You are initiating a Handshake!")


        arr_push = app.config['push']
        print "---------\n"
        payee_push = arr_push[0]
        print payee_push
        self.assertEqual(1, len(arr_push))
        self.assertEqual(payee_push['body'], 'You are initiating a Handshake.')

        """
        test case 2:
            scenerio:
                + handshake initiated
            expected:
                + trong1@autonomous.nyc will receive an email + push
                + trong2@autonomous.nyc will receive an email + push
        """
        print "------------------------------"
        print "--------- TEST CASE 2 --------"
        app.config['email'] = []
        app.config['push'] = []

        handshake_bl.send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['INTIATED'], source='web')

        arr = app.config['email']
        self.assertEqual(2, len(arr))

        payer = arr[0]
        payee = arr[1]

        print payer
        self.assertEqual(payer['content'], "<html><head><title>Handshake</title></head><body>You can view and respond at <a href='https://www.autonomous.ai/handshake>www.autonomous.ai/hanshake</a>, or simply use the Handshake mobile app to add your cryptographic signature. <br> Download Handshake for mobile on <a href='https://itunes.apple.com/us/app/crypto-handshake/id1360132818?ls=1&mt=8'>iOS</a> or <a href='https://play.google.com/store/apps/details?id=com.mobile_handshake'>Google play</a> <br> We will send you a status update once you are able to view and sign the agreement. <br><br> Handshake Team </body></html>")
        self.assertEqual(payer['from'], "trong1@autonomous.nyc")
        self.assertEqual(payer['to'], "trong2@autonomous.nyc")
        self.assertEqual(payer['subject'], "trong1@autonomous.nyc requires your cryptographic signature!")
        print "---------\n"
        print payee
        self.assertEqual(payee['content'], "<html><head><title>Handshake</title></head><body>Handshake with trong2@autonomous.nyc initiated! We have sent the other party a notification as well. You are now able to view its status in the app. </body></html>")
        self.assertEqual(payee['from'], "handshake@autonomous.nyc")
        self.assertEqual(payee['to'], "trong1@autonomous.nyc")
        self.assertEqual(payee['subject'], "You have initiated a Handshake!")


        arr_push = app.config['push']
        print "---------\n"
        payee_push = arr_push[0]
        payer_push = arr_push[1]
        print arr_push

        self.assertEqual(2, len(arr_push))
        self.assertEqual(payee_push['body'], 'You have initiated a Handshake!')
        self.assertEqual(payer_push['body'], 'You have an incoming Handshake.')


        """
        test case 3:
            scenerio:
                + handshake shaked
            expected:
                + trong1@autonomous.nyc will receive an email + push
                + trong2@autonomous.nyc will receive an email + push
        """
        print "------------------------------"
        print "--------- TEST CASE 3 --------"

        app.config['email'] = []
        app.config['push'] = []

        handshake_bl.send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['SHAKED'], source='web')

        arr = app.config['email']
        self.assertEqual(2, len(arr))

        payer = arr[0]
        payee = arr[1]

        print payer
        self.assertEqual(payer['content'], "<html><head><title>Handshake</title></head><body>trong1@autonomous.nyc is working on their side of the agreement. We will send you a status update when it has been delivered! <br></br> In the meantime, sign in to the app on <a href='https://www.autonomous.ai/handshake>www.autonomous.ai/hanshake</a>, or on mobile to view your Handshake details. </body></html>")
        self.assertEqual(payer['from'], "handshake@autonomous.nyc")
        self.assertEqual(payer['to'], "trong2@autonomous.nyc")
        self.assertEqual(payer['subject'], "Handshake: Contract in progress.")
        print "---------\n"
        print payee
        self.assertEqual(payee['content'], "<html><head><title>Handshake</title></head><body>trong2@autonomous.nyc signed your agreement! You now have deliverables pending. Sign in to the app on <a href='https://www.autonomous.ai/handshake>www.autonomous.ai/hanshake</a> or on mobile to view your Handshake and mark the task done.</body></html>")
        self.assertEqual(payee['from'], "handshake@autonomous.nyc")
        self.assertEqual(payee['to'], "trong1@autonomous.nyc")
        self.assertEqual(payee['subject'], "Your Handshake has been signed. Time to get to work!")


        arr_push = app.config['push']
        print "---------\n"
        payee_push = arr_push[0]
        payer_push = arr_push[1]
        print arr_push

        self.assertEqual(2, len(arr_push))
        self.assertEqual(payee_push['body'], 'Deliverables pending.')
        self.assertEqual(payer_push['body'], 'Contract in progress.')


        """
        test case 4:
            scenerio:
                + handshake deliver
            expected:
                + trong1@autonomous.nyc will receive an email + push
                + trong2@autonomous.nyc will receive an email + push
        """
        print "------------------------------"
        print "--------- TEST CASE 4 --------"

        app.config['email'] = []
        app.config['push'] = []

        handshake_bl.send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['DELIVER'], source='web')

        arr = app.config['email']
        self.assertEqual(2, len(arr))

        payer = arr[0]
        payee = arr[1]

        print payer
        self.assertEqual(payer['content'], "<html><head><title>Handshake</title></head><body> trong1@autonomous.nyc has completed their side of the agreement. You have 7 days to reject if you wish, after which they will automatically be able to withdraw their payment.</body></html>")
        self.assertEqual(payer['from'], "handshake@autonomous.nyc")
        self.assertEqual(payer['to'], "trong2@autonomous.nyc")
        self.assertEqual(payer['subject'], "Handshake: trong1@autonomous.nyc has delivered. 7 days to reject.")
        print "---------\n"
        print payee
        self.assertEqual(payee['content'], "<html><head><title>Handshake</title></head><body>Congrats! trong2@autonomous.nyc has been notified that you have completed your side of the agreement. They have a 7 day window to reject, after which you will be able to withdraw payment instantly.</body></html>")
        self.assertEqual(payee['from'], "handshake@autonomous.nyc")
        self.assertEqual(payee['to'], "trong1@autonomous.nyc")
        self.assertEqual(payee['subject'], "Handshake: Payment from trong2@autonomous.nyc available in 7 days.")


        arr_push = app.config['push']
        print "---------\n"
        payee_push = arr_push[0]
        payer_push = arr_push[1]
        print arr_push

        self.assertEqual(2, len(arr_push))
        self.assertEqual(payee_push['body'], 'Payment available in 7 days.')
        self.assertEqual(payer_push['body'], 'You have 7 days to reject.')

        """
        test case 5:
            scenerio:
                + handshake reject
            expected:
                + trong1@autonomous.nyc will receive an email + push
                + trong2@autonomous.nyc will receive an email + push
        """
        print "------------------------------"
        print "--------- TEST CASE 5 --------"

        app.config['email'] = []
        app.config['push'] = []

        handshake_bl.send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['REJECT'], source='web')

        arr = app.config['email']
        self.assertEqual(2, len(arr))

        payer = arr[0]
        payee = arr[1]

        print payer
        self.assertEqual(payer['content'], "<html><head><title>Handshake</title></head><body> We have sent a rejection notification to trong1@autonomous.nyc. They have 14 days to send a new offer or work for you to accept, after which the contract will terminate automatically. </body></html>")
        self.assertEqual(payer['from'], "handshake@autonomous.nyc")
        self.assertEqual(payer['to'], "trong2@autonomous.nyc")
        self.assertEqual(payer['subject'], "Handshake: You have 14 days to accept new work")
        print "---------\n"
        print payee
        self.assertEqual(payee['content'], "<html><head><title>Handshake</title></head><body>Sorry, trong2@autonomous.nyc has rejected your side of the agreement. The contract will be valid for 14 more days for you both to work it out or try again, after which it will terminate</body></html>")
        self.assertEqual(payee['from'], "handshake@autonomous.nyc")
        self.assertEqual(payee['to'], "trong1@autonomous.nyc")
        self.assertEqual(payee['subject'], "Handshake: Your offer has been rejected.")


        arr_push = app.config['push']
        print "---------\n"
        payee_push = arr_push[0]
        payer_push = arr_push[1]
        print arr_push

        self.assertEqual(2, len(arr_push))
        self.assertEqual(payee_push['body'], 'Your offer has been rejected.')
        self.assertEqual(payer_push['body'], 'You have 14 days to accept a new offer.')

        """
        test case 6:
            scenerio:
                + handshake done
            expected:
                + trong1@autonomous.nyc will receive an email + push
                + trong2@autonomous.nyc will receive an email + push
        """
        print "------------------------------"
        print "--------- TEST CASE 6 --------"

        app.config['email'] = []
        app.config['push'] = []

        handshake_bl.send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['DONE'], source='web')

        arr = app.config['email']
        self.assertEqual(2, len(arr))

        payer = arr[0]
        payee = arr[1]

        print payer
        self.assertEqual(payer['content'], "<html><head><title>Handshake</title></head><body> Congrats! Your Handshake with trong1@autonomous.nyc is complete </body></html>")
        self.assertEqual(payer['from'], "handshake@autonomous.nyc")
        self.assertEqual(payer['to'], "trong2@autonomous.nyc")
        self.assertEqual(payer['subject'], "Handshake: Complete!")
        print "---------\n"
        print payee
        self.assertEqual(payee['content'], "<html><head><title>Handshake</title></head><body> Congrats! Your Handshake with trong2@autonomous.nyc is complete </body></html>")
        self.assertEqual(payee['from'], "handshake@autonomous.nyc")
        self.assertEqual(payee['to'], "trong1@autonomous.nyc")
        self.assertEqual(payee['subject'], "Handshake: Complete!")


        arr_push = app.config['push']
        print "---------\n"
        payee_push = arr_push[0]
        payer_push = arr_push[1]
        print arr_push

        self.assertEqual(2, len(arr_push))
        self.assertEqual(payee_push['body'], 'Contract fulfilled!')
        self.assertEqual(payer_push['body'], 'Contract fulfilled!')

        """
        test case 7:
            scenerio:
                + handshake status whatever
            expected:
                + Do nothing
        """
        print "------------------------------"
        print "--------- TEST CASE 7 --------"

        app.config['email'] = []
        app.config['push'] = []

        handshake_bl.send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['SHAKE'], source='web')

        arr = app.config['email']
        self.assertEqual(0, len(arr))

        arr_push = app.config['push']
        self.assertEqual(0, len(arr_push))

if __name__ == '__main__':
    unittest.main()