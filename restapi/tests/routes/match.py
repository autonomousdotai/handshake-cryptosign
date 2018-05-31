from tests.routes.base import BaseTestCase
from mock import patch
from app.models import Device, Wallet
from app import db
from app.helpers.message import MESSAGE

import mock
import json
import time
import app.bl.user as user_bl

class TestMatchBluePrint(BaseTestCase):

    def setUp(self):
        pass

    def test_add_match(self):
        with self.client:
            pass

    def test_remove_match(self):
        with self.client:
            pass

    
if __name__ == '__main__':
    unittest.main()