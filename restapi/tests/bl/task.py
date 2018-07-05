#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from mock import patch
from datetime import datetime
from tests.routes.base import BaseTestCase
from app import db, app
from app.models import Task, User, Match, Outcome
from app.helpers.message import MESSAGE

import mock
import json
import time
import app.bl.task as task_bl

class TestTask(BaseTestCase):

    def setUp(self):
        # create match
        match = Match.find_match_by_id(1)
        if match is None:
            match = Match(
                id=1
            )
            db.session.add(match)
            db.session.commit()

    def clear_data_before_test(self):
        outcome1 = Outcome.find_outcome_by_id(10)
        outcome2 = Outcome.find_outcome_by_id(11)
        outcome3 = Outcome.find_outcome_by_id(12)
        outcome4 = Outcome.find_outcome_by_id(13)

        if outcome1 is not None:
            db.session.delete(outcome1)
            db.session.flush()

        if outcome2 is not None:
            db.session.delete(outcome2)
            db.session.flush()

        if outcome3 is not None:
            db.session.delete(outcome3)
            db.session.flush()

        if outcome4 is not None:
            db.session.delete(outcome4)
            db.session.flush()

        Task.query.delete()
        db.session.commit()
        

    def test_is_able_to_create_new_task_failed_if_time_less_than_5minutes(self):
        self.clear_data_before_test()

        outcome = Outcome(
            id=10,
            match_id=1,
            hid=88
        )
        db.session.add(outcome)
        db.session.commit()

        task = Task(
                    data=json.dumps({"odds": "2.7", "match_date": 1530767741, "match_name": "1 vs 2", "outcome_name": "Belgium wins (Handicap 0:2)", "hid": 17, "outcome_id": outcome.id, "side": 2}),
                    action='INIT',
                    date_created=datetime.now(),
                    date_modified=datetime.now()
                )
        db.session.add(task)
        db.session.commit()

        actual = task_bl.is_able_to_create_new_task(10)
        expected = False

        self.assertEqual(actual, expected)


    def test_is_able_to_create_new_task_passed_if_there_is_no_outcome_in_tasks(self):
        self.clear_data_before_test()

        outcome = Outcome(
            id=10,
            match_id=1,
            hid=88
        )
        db.session.add(outcome)
        db.session.commit()

        task = Task(
                    data=json.dumps({"odds": "2.7", "match_date": 1530767741, "match_name": "1 vs 2", "outcome_name": "Belgium wins (Handicap 0:2)", "hid": 17, "outcome_id": 122, "side": 2}),
                    action='INIT',
                    date_created=datetime.now(),
                    date_modified=datetime.now()
                )
        db.session.add(task)
        db.session.commit()

        actual = task_bl.is_able_to_create_new_task(outcome.id)
        expected = True

        self.assertEqual(actual, expected)


    def test_is_able_to_create_new_task_passed_if_time_is_large_than_5_minutes(self):
        self.clear_data_before_test()

        outcome = Outcome(
            id=10,
            match_id=1,
            hid=88
        )
        db.session.add(outcome)
        db.session.commit()

        task = Task(
                    data=json.dumps({"odds": "2.7", "match_date": 1530767741, "match_name": "1 vs 2", "outcome_name": "Belgium wins (Handicap 0:2)", "hid": 17, "outcome_id": outcome.id, "side": 2}),
                    action='INIT',
                    date_created=datetime(2018, 6, 18),
                    date_modified=datetime(2018, 6, 18)
                )
        db.session.add(task)
        db.session.commit()

        actual = task_bl.is_able_to_create_new_task(outcome.id)
        expected = True

        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()