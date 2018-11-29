from tests.routes.base import BaseTestCase
from mock import patch
from app import db
from app import app
from app.models import Redeem
from app.helpers.message import MESSAGE
import mock
import json

class TestRedeem(BaseTestCase):
    
    def clear_data_before_test(self):
        pass

    def test_find_redeem_uppercase_and_lowercase(self):
        Uid = 66
        redeem_code = "A1b2C3d4E5"
        redeem = Redeem(
            code=redeem_code
        )
        db.session.add(redeem)
        db.session.commit()

        redeem1 = Redeem.find_redeem_by_code(redeem_code)

        self.assertTrue(redeem1 != None)

        redeem2 = Redeem.find_redeem_by_code("a1b2C3d4e5")
        self.assertTrue(redeem2 == None)

        db.session.delete(redeem)
        db.session.commit()


    def test_check_redeem_code(self):
        code = 'ABC'
        r = Redeem.find_redeem_by_code(code)
        if r is None:
            redeem = Redeem(
                code=code
            )
            db.session.add(redeem)
            db.session.commit()
        else:
            r.reserved_id = 88
            r.used_user = 0
            db.session.commit()

        with self.client:
            Uid = 88
            params = {
                "redeem": "Abc"
            }
            response = self.client.post(
                                    '/redeem/check',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)

            # recheck again
            params = {
                "redeem": "ABC"
            }
            response = self.client.post(
                                    '/redeem/check',
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