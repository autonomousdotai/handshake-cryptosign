from tests.routes.base import BaseTestCase
from mock import patch
from app.models import Device, Tx, Handshake
from app import db, app
from app.helpers.message import MESSAGE
from app.constants import Handshake as HandshakeStatus

import mock
import json
import time
import app.bl.user as user_bl

class TestEventBluePrint(BaseTestCase):

    def setUp(self):
        pass

    def test_reiceive_init_event(self):
        pass

    def test_reiceive_uninit_event(self):
        pass
    
if __name__ == '__main__':
    unittest.main()