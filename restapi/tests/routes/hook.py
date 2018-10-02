# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app import db, app
from app.models import User
from sqlalchemy import bindparam, literal_column, func
from app.helpers.message import MESSAGE

import mock
import json


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

if __name__ == '__main__':
    unittest.main()
