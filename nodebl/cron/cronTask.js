
const cron = require('node-cron');
const configs = require('../configs');
const web3 = require('../configs/web3');

// daos
const taskDAO = require('../daos/task');
const settingDAO = require('../daos/setting');
const onchainDataDAO = require('../daos/onchainTask');

const constants = require('../constants');
const utils = require('../libs/utils');
const network_id = configs.network_id;
const ownerAddress = configs.network[network_id].ownerAddress;
const amountDefaultValue = configs.network[network_id].amountValue;

let isRunningTask = false;


/**
 * 
 * @param {array} arr
 * * @param {object} onchainData
 * * @param {object} task
 */								
const saveTnxs = (arr) => {
	return new Promise((resolve, reject) => {
		const tnxs = [];
		(arr || []).forEach(item => {
			if (item.onchainData) {
				tnxs.push({
					contract_name: item.contract_name,
					contract_address: item.contract_address,
					contract_method: item.onchainData.contract_method,
					is_erc20: item.is_erc20 || 0,
					from_address: item.onchainData.from_address,
					description: item.onchainData.description || 'cron tnx',
					data: JSON.stringify(item),
					status: -1,
					task_id: item.task.id,
					deleted: 0
				});
			}
		});
		onchainDataDAO.multiInsert(tnxs).then(resolve).catch(reject);
	});
};

/**
 * 
 * @param {number} params.hid
 * @param {number} params.side
 * @param {string} params.maker
 * @param {number} params.outcome_result
 * @param {string} params.offchain
 */
const unInitFreeBet = (params) => {
	return new Promise((resolve, reject) => {
		return resolve([{
			contract_method: 'uninitForTrial',
			hid: params.hid,
			side: params.side,
			odds: parseInt(params.odds * 100),
			maker: params.maker,
			value: params.value,
			offchain: params.offchain
		}])
	});
};

/**
 * 
 * @param {number} params.odds
 * @param {number} params.outcome_id
 * @param {number} params.side
 * @param {number} params.hid
 * @param {number} params.match_date
 * @param {string} params.match_name
 * @param {string} params.outcome_name
 * @param {number} params.type
 * @param {address} params.from_address
 * @param {Object} task
 * @param {boolean} isFreeBet
 */
const initBet = (params, task, isFreeBet) => {
	return new Promise(async (resolve, reject) => {
		try {

			if (params.hid == null || params.hid == 'null' || params.hid == undefined) {
				console.log(`NOT FOUND HID, UPDATE TASK'S STATUS TO: WAITING`);
				await taskDAO.updateStatusById(task, constants.TASK_STATUS.STATUS_WAITING_ONCHAIN_HID)
				return resolve(undefined);
			}

			const dataRequest = {
				type: params.type || 3,
				extra_data: utils.gennerateExtraData(params.match_date, params.match_name, params.outcome_name),
				outcome_id: params.outcome_id,
				odds: params.odds, // TODO: check value 
				amount: amountDefaultValue + '',
				currency: 'ETH',
				side: params.side,
				from_address: params.from_address || ownerAddress, // TODO: check this address
				hid: params.hid,
				isFreeBet: isFreeBet,
				payload: params.payload,
				is_free_bet: params.free_bet,
				uid: params.uid
			};

			utils.submitInitAPI(dataRequest)
			.then(results => {
				return resolve(results);
			})
			.catch(err => {
				return reject(err);
			});
		} catch (e) {
			console.log('initRealBet error: ', e);
			reject({
				err_type: constants.TASK_STATUS.INIT_REAL_BET_EXCEPTION,
				options_data: { params }
			});
		}
	});
};

/**
 * @param {string} params.offchain
 * @param {number} params.hid
 * @param {number} params.outcome_result
 * @param {string} params.offchain
 */

const report = (params) => {
	return new Promise((resolve, reject) => {
		return resolve([{
			contract_method: 'reportOutcomeTransaction',
			hid: params.hid,
			outcome_result: params.outcome_result,
			offchain: params.offchain
		}])
	});
};

/**
 * @param {number} params.hid
 * @param {string} params.winner
 * @param {string} params.offchain
 */
const collect = (params) => {
	return new Promise((resolve, reject) => {
		return resolve([{
			contract_method: 'collectTestDrive',
			hid: params.hid,
			winner: params.winner,
			offchain: params.offchain
		}])
	});
};

/**
 * @param {number} params.disputeTime
 * @param {number} params.reportTime
 * @param {number} params.date
 * @param {string} params.source
 * @param {number} params.market_fee
 * @param {number} params.id
 * @param {array} params.outcomes
 * * @param {number} outcomes.result
 * * @param {number} outcomes.public
 * * @param {number} outcomes.hid
 * * @param {string} outcomes.name
 * 
 */
const createMarket = (params) => {
	return new Promise((resolve, reject) => {
		if (params.date < params.reportTime && params.reportTime < params.disputeTime) {
			return resolve(utils.generateMarkets(params.outcomes, params.market_fee, params.date, params.disputeTime, params.reportTime, params.source));
		}
		return reject({
			err_type: constants.TASK_STATUS.CREATE_MARKET_TIME_INVALID,
			options_data: { date: params.date, disputeTime: params.disputeTime, reportTime: params.reportTime }
		});
	});
}

const asyncScanTask = () => {
	return new Promise((resolve, reject) => {
		const tasks = [];
		taskDAO.getTasksByStatus()
		.then(_tasks => {
			_tasks.forEach(task => {
				if (task && task.task_type && task.data) {
					tasks.push(
						new Promise((resolve, reject) => {
							taskDAO.updateStatusById(task, constants.TASK_STATUS.STATUS_PROGRESSING)
							.then( resultUpdate => {
								const params = JSON.parse(task.data)
								let processTaskFunc = undefined;
								let contract_name = '';
								let contract_address = '';
								switch (task.task_type) {
									case 'REAL_BET': // ETHER
										contract_name = 'PredictionHandshake';
										contract_address = configs.network[network_id].bettingHandshakeAddress;

										switch (task.action) {
											case 'INIT':
												processTaskFunc = initBet(params, task, false);
											break;
											case 'REPORT':
												processTaskFunc = report(params);
											break;
											case 'CREATE_MARKET':
												processTaskFunc = createMarket(params);
											break;
										}
									break;

									case 'FREE_BET': // ETHER
										contract_name = 'PredictionHandshake';
										contract_address = configs.network[network_id].bettingHandshakeAddress;

										switch (task.action) {
											case 'INIT':
												processTaskFunc = initBet(params, task, true);
											break;
											case 'UNINIT':
												processTaskFunc = unInitFreeBet(params);
											break;
											case 'COLLECT':
												processTaskFunc = collect(params);
											break;
										}
									break;

									case 'ERC_20':
										contract_name = '';
										contract_address = '';
									break;
								}

								if (!processTaskFunc) {
									return reject({
										err_type: constants.TASK_STATUS.TASK_TYPE_NOT_FOUND,
										options_data: {
											task: task.toJSON()
										}
									});
								}
			
								processTaskFunc
								.then(result => {
									return resolve({
										contract_name: contract_name,
										contract_address: contract_address,
										onchainData: result,
										task: task.toJSON()
									});
								})
								.catch(err => {
									utils.handleErrorTask(task, err.err_type);
									return reject(err);
								});
							})
							.catch(err => {
								return reject({
									err_type: constants.TASK_STATUS.UPDATE_TASK_STATUS_FAIL,
									error: err,
									options_data: {
										task: task.toJSON()
									}
								});
							})
						})
					);
				} else {
					console.error('Task is empty with id: ', task.id);
				}
			});

			Promise.all(tasks)
			.then(results => {
				console.log('START SUBMIT MULTI TRANSACTION!');
				let tnxs = [];
				(results || []).forEach(i => {
					if (Array.isArray(i.onchainData)) {
						i.onchainData.forEach(tnxData => {
							if (tnxData.contract_method) {
								tnxs.push({
									contract_name: i.contract_name,
									contract_address: i.contract_address,
									onchainData: tnxData,
									task: i.task
								});
							}
						});
					}
				});

				saveTnxs(tnxs)
				.then(tnxResults => {
					console.log('SUBMIT MULTI TNX DONE WITH RESULT: ', tnxResults.length);

					if (Array.isArray(tnxResults) && tnxResults.length > 0) {
						web3.setNonce( web3.getNonce() + tnxResults.length);
						const taskIds = tnxResults.map(i => { return i.task_id; })
						
						console.log('UPDATE TASK STATUS ', taskIds);
						taskDAO.multiUpdateStatusById(taskIds, constants.TASK_STATUS.STATUS_SUCCESS)
						.then(updateResults => {
							return resolve(tnxResults);
						})
						.catch(err => {
							console.error('Error update task status: ', err);
							return reject(err);
						})
					} else {
						resolve([]);
					}
				})
				.catch(err => {
					console.error('Error', err);
					return reject(err);
				});
			})
			.catch(err => {
				console.error('Error', err);
				return reject(err);
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
					console.log('task cron done at ' + new Date());
					console.log('EXIT SCAN TASK');
					isRunningTask = false;
				})
				.catch(e => {
					isRunningTask = false;
					console.error(e);
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
