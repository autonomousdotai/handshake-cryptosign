#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from mock import patch
from app import db, app
from app.models import Tx, Handshake, Shaker
from app.helpers.utils import local_to_utc

import app.bl.event as event_bl
import app.constants as CONST
import mock
import json


class TestEventBl(BaseTestCase):

    def clear_data_before_test(self):
        pass

    def test_run_bots_for_tx_with_init_method(self):
        self.clear_data_before_test()

		# -----
        handshake = Handshake(
            hs_type=3,
            chain_id=4,
            user_id=88,
            outcome_id=88,
            odds=1.1,
            amount=1,
            currency='ETH',
            side=1,
            remaining_amount=1,
            from_address='0x1234',
            status=0
		)
        db.session.add(handshake)
        db.session.commit()

        # add tx
        tx = Tx(
            contract_method='init',
            offchain='cryptosign_m{}'.format(handshake.id)
        )
        db.session.add(tx)
        db.session.commit()


        actual = event_bl.run_bots_for_tx(tx, debug=True)
        expected = handshake.outcome_id
        self.assertEqual(actual, expected)

        # add tx
        tx = Tx(
            contract_method='initTestDrive',
            offchain='cryptosign_m{}'.format(handshake.id)
        )
        db.session.add(tx)
        db.session.commit()


        actual = event_bl.run_bots_for_tx(tx, debug=True)
        expected = handshake.outcome_id
        self.assertEqual(actual, expected)


    def test_run_bots_for_tx_with_shake_method(self):
        self.clear_data_before_test()

		# -----
        handshake = Handshake(
            hs_type=3,
            chain_id=4,
            user_id=88,
            outcome_id=88,
            odds=1.1,
            amount=1,
            currency='ETH',
            side=1,
            remaining_amount=1,
            from_address='0x1234',
            status=0
		)
        db.session.add(handshake)
        db.session.commit()

        # add shaker
        shaker = Shaker(
            shaker_id=66,
            amount=0.2,
            currency='ETH',
            odds=6,
            side=1,
            handshake_id=handshake.id,
            from_address='0x123',
            chain_id=4,
            status=-1
        )
        db.session.add(shaker)
        db.session.commit()

        # add tx
        tx = Tx(
            contract_method='shake',
            offchain='cryptosign_s{}'.format(shaker.id)
        )
        db.session.add(tx)
        db.session.commit()


        actual = event_bl.run_bots_for_tx(tx, debug=True)
        expected = handshake.outcome_id
        self.assertEqual(actual, expected)


        # add tx
        tx = Tx(
            contract_method='shakeTestDrive',
            offchain='cryptosign_s{}'.format(shaker.id)
        )
        db.session.add(tx)
        db.session.commit()


        actual = event_bl.run_bots_for_tx(tx, debug=True)
        expected = handshake.outcome_id
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()