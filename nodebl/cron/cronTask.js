
const cron = require('node-cron');
const configs = require('../configs');

// daos
const taskDAO = require('../daos/task');
const settingDAO = require('../daos/setting');

const constants = require('../constants');
const utils = require('../libs/utils');
const predictionContract = require('../libs/smartcontract');
const network_id = configs.network_id;
const ownerAddress = configs.network[network_id].ownerAddress;
const amountDefaultValue = configs.network[network_id].amountValue;

let isRunningTask = false;


const submitMultiTnx = (arr) => {
	return new Promise((resolve, reject) => {
		predictionContract.getNonce(ownerAddress, 'pending')
		.then(nonce => {
			console.log('Current nonce pending: ', nonce);
			let tasks = [];
			let index = 0;
			arr.forEach((item) => {
				let smartContractFunc = null;
				const onchainData = item.onchainData;
				switch (onchainData.contract_method) {
					case 'createMarket':
						smartContractFunc = predictionContract.createMarketTransaction(nonce + index, onchainData.fee, onchainData.source, onchainData.closingTime, onchainData.reportTime, onchainData.disputeTime, onchainData.offchain, item);
					break;
					case 'init':
						smartContractFunc = predictionContract.submitInitTransaction(nonce + index, onchainData.hid, onchainData.side, onchainData.odds, onchainData.offchain, onchainData.value, item);
					break;
					case 'shake':
						smartContractFunc = predictionContract.submitShakeTransaction(onchainData.hid, onchainData.side, onchainData.odds, onchainData.maker, onchainData.offchain, parseFloat(onchainData.amount), nonce + index, item);
					break;
					case 'collectTestDrive':
						smartContractFunc = predictionContract.submitCollectTestDriveTransaction(onchainData.hid, onchainData.winner, onchainData.offchain, nonce + index, item);
					break;
					case 'reportOutcomeTransaction':
						smartContractFunc = predictionContract.reportOutcomeTransaction(onchainData.hid, onchainData.outcome_result, nonce + index, onchainData.offchain, item);
					break;
					case 'initTestDriveTransaction':
						smartContractFunc = predictionContract.submitInitTestDriveTransaction(onchainData.hid, onchainData.side, onchainData.odds, onchainData.maker, onchainData.offchain, parseFloat(onchainData.amount), nonce + index, item);
					break;
					case 'shakeTestDriveTransaction':
						smartContractFunc = predictionContract.submitShakeTestDriveTransaction(onchainData.hid, onchainData.side, onchainData.taker, onchainData.takerOdds, onchainData.maker, onchainData.makerOdds, onchainData.offchain, parseFloat(onchainData.amount), nonce + index, item);
					break;
					case 'uninitForTrial':
						smartContractFunc = predictionContract.uninitForTrial(onchainData.hid, onchainData.side, onchainData.odds, onchainData.maker, `${onchainData.value}`, onchainData.offchain, nonce + index, item);
					break;
				}
				index += 1;
				tasks.push(smartContractFunc);
			});
			Promise.all(tasks)
			.then(result => {
				return resolve(result);
			})
			.catch(err => {
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
		if (params.date && params.date < params.disputeTime && params.disputeTime < params.reportTime) {
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
								switch (task.task_type) {
									case 'REAL_BET':
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

									case 'FREE_BET':
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
				results.forEach(i => {
					if (Array.isArray(i.onchainData)) {
						i.onchainData.forEach(tnxData => {
							tnxs.push({
								onchainData: tnxData,
								task: i.task
							});
						});
					}
				});

				submitMultiTnx(tnxs)
				.then(tnxResults => {
					console.log('SUBMIT MULTI TNX DONE WITH RESULT: ');
					console.log(tnxResults);

					if (Array.isArray(tnxResults) && tnxResults.length > 0) {
						const taskIds = tnxResults.map(i => { return i.task.id; })

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
				})
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
