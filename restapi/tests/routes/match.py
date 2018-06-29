from tests.routes.base import BaseTestCase
from mock import patch
from app import db
from app.helpers.message import MESSAGE

import mock
import json
import time

class TestMatchBluePrint(BaseTestCase):

    def setUp(self):
        pass

    def test_get_match_with_public(self):
        with self.client:
            pass

    def test_get_match_with_private(self):
        with self.client:
            pass

    
if __name__ == '__main__':
    unittest.main()