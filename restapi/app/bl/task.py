from flask import g
from datetime import datetime, timedelta
from app import db
from app.models import Task
from sqlalchemy import and_

import time
import json

def is_able_to_create_new_task(outcome_id):
	tasks = db.session.query(Task).filter(and_(Task.action == 'INIT', (Task.date_created + timedelta(seconds=300)) > datetime.now())).order_by(Task.date_created.desc()).all()
	if tasks is not None:
		for task in tasks:
			try:
				j = json.loads(task.data)
				if int(j['outcome_id']) == int(outcome_id):
					n = time.mktime(datetime.now().timetuple())
					ds = time.mktime(task.date_created.timetuple())
					if n - ds > 300:
						return True

					print '----- WTF -----'
					print '{} {}'.format(n, ds)
					return False
			except Exception as ex:
				print(str(ex))
	return True
	