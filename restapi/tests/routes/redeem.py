from tests.routes.base import BaseTestCase
from mock import patch
from app import db
from app import app
from app.models import Redeem
from app.helpers.message import MESSAGE
import mock
import json

class TestRedeem(BaseTestCase):

    def setUp(self):
        pass

    def clear_data_before_test(self):
        pass

    def test_add_outcome(self):
        with self.client:
            pass

    def test_find_redeem_uppercase_and_lowercase(self):
        Uid = 66
        redeem_code = "A1b2C3d4E5"
        redeem = Redeem(
            code=redeem_code
        )
        db.session.add(redeem)
        db.session.flush()
        db.session.commit()

        redeem1 = Redeem.find_redeem_by_code(redeem_code)

        self.assertTrue(redeem1 != None)

        redeem2 = Redeem.find_redeem_by_code("a1b2C3d4E5")
        self.assertTrue(redeem2 == None)

        db.session.delete(redeem)
        db.session.commit()


if __name__ == '__main__':
    unittest.main()