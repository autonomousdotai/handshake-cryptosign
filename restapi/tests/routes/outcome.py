from tests.routes.base import BaseTestCase
from mock import patch
from app import db
from app import app
from app.models import Match, Outcome, Source
from app.helpers.message import MESSAGE
import mock
import json
import time
import jwt
import app.bl.user as user_bl

from datetime import datetime
from app.helpers.utils import local_to_utc

class TestOutcomeBluePrint(BaseTestCase):

    def setUp(self):
        # create match
        match = Match.find_match_by_id(1)
        if match is None:
            match = Match(
                id=1
            )
            db.session.add(match)
            db.session.commit()

        # create outcome
        outcome = Outcome.find_outcome_by_id(88)
        if outcome is None:
            outcome = Outcome(
                id=88,
                match_id=1,
                name="1",
                hid=88,
                created_user_id=66
            )
            db.session.add(outcome)
            db.session.commit()

        else:
            outcome.name = "1"
            outcome.created_user_id = 66
            db.session.commit()


    def clear_data_before_test(self):
        pass

    def test_add_outcome(self):
        with self.client:
            pass

    def test_remove_outcome(self):
        with self.client:
            pass

    def test_generate_link(self):
        Uid = 66
        # create outcome
        outcome = Outcome.find_outcome_by_id(88)
        if outcome is None:
            outcome = Outcome(
                id=88,
                match_id=1,
                name="1",
                hid=88,
                created_user_id=Uid
            )
            db.session.add(outcome)
            db.session.commit()

        else:
            outcome.match_id =1
            outcome.name = "1"
            outcome.created_user_id = Uid
            db.session.commit()
    
        with self.client:

            params = {
                "match_id": 1
            }
            response = self.client.post(
                                    '/outcome/generate-link',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            data_json = data['data']
            self.assertTrue(data['status'] == 1)
            self.assertTrue(data_json['slug'] == '?match=1&ref=66')

    def test_add_outcome(self):
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        arr_match=[]
        Uid = 66
        source1 = Source.find_source_by_id(1)
        if source1 is None:
            source1 = Source(
                id = 1,
                name = "Source",
                url = "htpp://www.abc.com",
                approved = 1
            )
            db.session.add(source1)
            db.session.commit()

        match = Match.find_match_by_id(1000)
        if match is not None:
            match.date=seconds + 100
            match.reportTime=seconds + 200
            match.disputeTime=seconds + 300
            match.public=1
            match.source_id=source1.id
            db.session.flush()
            arr_match.append(match)

        else:
            match = Match(
                id=1000,
                public=1,
                date=seconds + 100,
                reportTime=seconds + 200,
                disputeTime=seconds + 300,
                source_id=source1.id
            )
            arr_match.append(match)
            db.session.add(match)
        db.session.commit()

        # create outcome
        outcome = Outcome.find_outcome_by_id(888)
        if outcome is None:
            outcome = Outcome(
                id=888,
                match_id=match.id,
                name="1",
                hid=88,
                created_user_id=Uid
            )
            db.session.add(outcome)
            arr_match.append(outcome)
            db.session.commit()

        else:
            outcome.match_id =match.id
            outcome.name = "1"
            outcome.created_user_id = Uid
            db.session.commit()
    
        with self.client:

            params = [
                {
                    "name": "outcome test",
                    "match_id": match.id,
                    "hid": 88
                }
            ]
            response = self.client.post(
                                    '/outcome/add/{}'.format(match.id),
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            data_json = data['data']
            self.assertTrue(data['status'] == 1)

            for item in arr_match:
                db.session.delete(item)
                db.session.commit()


if __name__ == '__main__':
    unittest.main()