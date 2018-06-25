
const cron = require('node-cron');
const configs = require('../configs');

// daos
const taskDAO = require('../daos/task');
const settingDAO = require('../daos/setting');

const utils = require('../libs/utils');
const predictionContract = require('../libs/smartcontract');
const network_id = configs.network_id;
const ownerAddress = configs.network[network_id].ownerAddress;

const web3 = require('../configs/web3').getWeb3();
let isRunningTask = false;


const submitMultiTnx = (arr) => {
	return new Promise((resolve, reject) => {
		predictionContract.getNonce(ownerAddress)
		.then(nonce => {
			let tasks = [];
			let index = 0;
			arr.forEach((item) => {
				let smartContractFunc = null;
				switch (item.contract_method) {
					case 'init':
						smartContractFunc = predictionContract.submitInitTransaction(nonce + index, item.hid, item.side, item.odds, item.offchain, item.value);
						index += 1;
					break;
					case 'collectTestDrive':
						smartContractFunc = predictionContract.submitCollectTestDriveTransaction(item.hid, item.winner, item.offchain, nonce + index);
						index += 1;
					break;
					case 'reportOutcomeTransaction':
						smartContractFunc = predictionContract.reportOutcomeTransaction(item.hid, item.outcome_result, nonce + index);
						index += 1;
					break;
				}
				tasks.push(smartContractFunc);
			});
			Promise.all(tasks)
			.then(result => {
				// TODO
				return resolve();
			})
			.catch(err => {
				// TODO
				return reject(err);
			})
		})
		.catch(err => {
			return reject(err);
		})
	});
}

/**
 * 
 * @param {number} params.type
 * @param {JSON string} params.extra_data
 * @param {number} params.outcome_id
 * @param {number} params.odds
 * @param {number} params.amount
 * @param {string} params.currency
 * @param {number} params.side
 * @param {string} params.from_address
 */
const init = (params) => {
	return new Promise((resolve, reject) => {
		utils.submitInitAPI(params)
		.then(result => {
			return resolve(Object.assign(result, {
				contract_method: 'init'
			}))
		})
		.catch(err => {
			//TODO: handle error
			return reject(err);
		})
	});
};

const unInit = (params) => {
	return new Promise((resolve, reject) => {
	});
};

/**
 * @param {number} params.hid
 * @param {number} outcome_result
 */
const report = (params) => {
	return new Promise((resolve, reject) => {
		return resolve({
			contract_method: 'reportOutcomeTransaction',
			hid: params.hid,
			outcome_result: params.outcome_result
		})
	});
};

/**
 * @param {number} params.hid
 * @param {string} params.winner
 * @param {string} params.offchain
 */
const collect = (params) => {
	return new Promise((resolve, reject) => {
		return resolve({
			contract_method: 'collectTestDrive',
			hid: params.hid,
			winner: params.winner,
			offchain: params.offchain
		})
	});
};

const asyncScanTask = () => {
	return new Promise((resolve, reject) => {
		const tasks = [];
		taskDAO.getTasksByStatus()
		.then(_tasks => {
			_tasks.forEach(task => {
				tasks.push(
					new Promise((resolve, reject) => {
						
						if (!task || !task.task_type) {
							return reject('Task is empty');
						}
	
						if (task.data) {
							return reject('Task params is empty');
						}
	
						const params = JSON.parse(task.data)
						let processTaskFunc = undefined;
	
						switch(task.task_type){
							case 'INIT':
								processTaskFunc = init(params);
							break;
							case 'UNINIT':
								processTaskFunc = unInit(params);
							break;
							case 'COLLECT':
								processTaskFunc = collect(params);
							break;
							case 'REPORT':
								processTaskFunc = report(params);
							break;
						}
	
						processTaskFunc
						.then(result => {
							return resolve(result);
							console.log('======');
						})
						.catch(err => {
							return reject(err);
						})
					})
				)
			});

			Promise.all(tasks)
			.then(results => {
				console.log('Done');
				submitMultiTnx(results)
				.then(tnxResults => {
					console.log(tnxResults);
				})
				.catch(err => {
					console.error('Error', err);
				})	
			})
			.catch(err => {
				console.error('Error', err);
			})
		});
	})
};

const runTaskCron = () => {
    cron.schedule('*/5 * * * * *', async () => {
		console.log('task cron running a task every 5s at ' + new Date());
		try {
			const setting = await settingDAO.getByName('TaskCronJob');
				if (!setting) {
					console.log('TaskCronJob setting is null. Exit!');
					return;
				}
				if(!setting.status) {
					console.log('Exit TaskCronJob setting with status: ' + setting.status);
					return;
				}
				console.log('Begin run TaskCronJob!');

			if (isRunningTask === false) {
				isRunningTask = true;
				
				asyncScanTask()
				.then(results => {
					console.log('EXIT SCAN TASK: ', result);
					isRunningTask = false;
				})
				.catch(e => {
					throw e;
				})

			} else {
        console.log('CRON JOB SCAN TASK IS RUNNING!');
			}
		} catch (e) {
			isRunningTask = false;
			console.log('cron task error');
			console.error(e);
		}
	});
};

module.exports = { runTaskCron };
