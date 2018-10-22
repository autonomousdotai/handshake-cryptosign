
from app.models import Task

import json
import app.constants as CONST
import app.bl.contract as contract_bl


def add_create_market_task(match):
	# get active contract
	contract = contract_bl.get_active_smart_contract()
	if contract is None:
		return None

	# add task
	task = Task(
		task_type=CONST.TASK_TYPE['REAL_BET'],
		data=json.dumps(match.to_json()),
		action=CONST.TASK_ACTION['CREATE_MARKET'],
		status=-1,
		contract_address=contract.contract_address,
		contract_json=contract.json_name
	)
	return task