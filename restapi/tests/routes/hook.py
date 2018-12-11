# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app import db, app
from app.models import User, Match, Outcome
from sqlalchemy import bindparam, literal_column, func
from app.helpers.message import MESSAGE
from app.helpers.utils import local_to_utc
from datetime import datetime
        
import mock
import json
import app.constants as CONST


class TestHookBluePrint(BaseTestCase):

    def test_hook_update_user(self):
        # Test email is valid
        user = User.find_user_with_id(1)
        email = "abc123456@abc123456.com"
        if user is None:
            user = User(
                id=1
            )
            db.session.add(user)
        else:
            user.email = None
            
        db.session.commit()

        with self.client:
            params = {
                "type_change": "Update",
                "user_id": user.id,
                "email": email,
                "meta_data": ""
            }

            response = self.client.post(
                                    '/hook/dispatcher',
                                    data=json.dumps(params), 
                                    content_type='application/json'
                                    )

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            user = User.find_user_with_id(1)
            self.assertTrue(user.email == email)

        # Test email is null
        with self.client:
            params = {
                "type_change": "Update",
                "user_id": user.id,
                "email": None,
                "meta_data": ""
            }

            response = self.client.post(
                                    '/hook/dispatcher',
                                    data=json.dumps(params), 
                                    content_type='application/json'
                                    )

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            user = User.find_user_with_id(1)
            self.assertTrue(user.email == email)

        # Test email with different email
        with self.client:
            email2 = "abc789@abc789.com"
            params = {
                "type_change": "Update",
                "user_id": user.id,
                "email": email2,
                "meta_data": ""
            }

            response = self.client.post(
                                    '/hook/dispatcher',
                                    data=json.dumps(params), 
                                    content_type='application/json'
                                    )

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            user = User.find_user_with_id(1)
            self.assertTrue(user.email == email2)


    def test_hook_update_comment_count(self):
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)

        match = Match.find_match_by_id(4685)
        if match is not None:
            match.date = seconds + 100
            match.reportTime = seconds + 200
            match.disputeTime = seconds + 300
            match.source_id = 3
        else:
            match = Match(
                id=4685,
                public=1,
                date=seconds + 100,
                reportTime=seconds + 200,
                disputeTime=seconds + 300,
                source_id = 3
            )
            db.session.add(match)
        db.session.commit()

        # Test email is null
        with self.client:
            params = {
                "commentNumber": 8,
                "objectId": 'outcome_id_4685'
            }

            response = self.client.post(
                                    '/hook/comment-count',
                                    data=json.dumps(params), 
                                    content_type='application/json'
                                    )

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)


    def test_hook_slack_command(self):
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)

        match = Match.find_match_by_id(4685)
        if match is not None:
            for o in match.outcomes:
                db.session.delete(o)
                db.session.commit()
            db.session.delete(match)
            db.session.commit()
    
        match = Match(
            id=4685,
            public=1,
            date=seconds + 100,
            reportTime=seconds + 200,
            disputeTime=seconds + 300,
            source_id = 3
        )
        db.session.add(match)
        db.session.commit()

        outcome = Outcome(
            match_id=match.id,
            name="test approve",
            approved=CONST.OUTCOME_STATUS['PENDING']
        )
        db.session.add(outcome)
        db.session.commit()

        with self.client:
            url_query_str = """token=ABC123&team_id=T0001&team_domain=example&channel_id=C123456&channel_name=test&user_id=U123456&user_name=Steve&command=%2Fweather&text={}_{}&response_url=https://hooks.slack.com/commands/1234/5678""".format(match.id, 1)
            response = self.client.get(
                '/hook/slack/command?{}'.format(url_query_str)
            )

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

        # Case: outcome was approved or rejected
        match = Match.find_match_by_id(4685)
        if match is not None:
            for o in match.outcomes:
                db.session.delete(o)
                db.session.commit()
            db.session.delete(match)
            db.session.commit()
    
        match = Match(
            id=4685,
            public=1,
            date=seconds + 100,
            reportTime=seconds + 200,
            disputeTime=seconds + 300,
            source_id = 3
        )
        db.session.add(match)
        db.session.commit()

        outcome = Outcome(
            match_id=match.id,
            name="test approve",
            # hid=1
            approved=CONST.OUTCOME_STATUS['APPROVED']
        )
        db.session.add(outcome)
        db.session.commit()

        with self.client:
            url_query_str = """token=ABC123&team_id=T0001&team_domain=example&channel_id=C123456&channel_name=test&user_id=U123456&user_name=Steve&command=%2Fweather&text={}_{}&response_url=https://hooks.slack.com/commands/1234/5678""".format(match.id, 1)
            response = self.client.get(
                '/hook/slack/command?{}'.format(url_query_str)
            )

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] != 1)

        # Case: time invalid
        match = Match.find_match_by_id(4685)
        if match is not None:
            for o in match.outcomes:
                db.session.delete(o)
                db.session.commit()
            db.session.delete(match)
            db.session.commit()
    
        match = Match(
            id=4685,
            public=1,
            date=seconds - 100,
            reportTime=seconds + 200,
            disputeTime=seconds + 300,
            source_id = 3
        )
        db.session.add(match)
        db.session.commit()

        outcome = Outcome(
            match_id=match.id,
            name="test approve",
            # hid=1
            approved=CONST.OUTCOME_STATUS['APPROVED']
        )
        db.session.add(outcome)
        db.session.commit()

        with self.client:
            url_query_str = """token=ABC123&team_id=T0001&team_domain=example&channel_id=C123456&channel_name=test&user_id=U123456&user_name=Steve&command=%2Fweather&text={}_{}&response_url=https://hooks.slack.com/commands/1234/5678""".format(match.id, 1)
            response = self.client.get(
                '/hook/slack/command?{}'.format(url_query_str)
            )

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)

        for o in match.outcomes:
            db.session.delete(o)
            db.session.commit()
        db.session.delete(match)
        db.session.commit()

if __name__ == '__main__':
    unittest.main()
