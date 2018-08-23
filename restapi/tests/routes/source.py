# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app.models import Source
from app import db, app
from app.helpers.message import MESSAGE

import mock
import json
import time

class TestSourceBluePrint(BaseTestCase):
            
    def setUp(self):
        # create source
        source = Source.find_source_by_id(1)
        if source is None:
            source = Source(
                id=1,
                name="source1",
                url="url1"
            )
            db.session.add(source)
            db.session.commit()
        
        else:
            source.name = "source1"
            source.url = "url1"
            db.session.flush()
            db.session.commit()

    def tearDown(self):
        pass

    def clear_data_before_test(self):
        pass

    def test_validate_source(self):
        with self.client:
            Uid = 66
            params = {
                "name": "1",
                "url": ""
            }
            response = self.client.post(
                                    '/source/validate',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            "---> case 2:"

            params = {
                "name": "source1",
                "url": "url1"
            }
            response = self.client.post(
                                    '/source/validate',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
    
if __name__ == '__main__':
    unittest.main()