
const cron = require('node-cron');
const configs = require('../configs');
const moment = require('moment');
const web3 = require('../configs/web3');

// daos
const taskDAO = require('../daos/task');
const settingDAO = require('../daos/setting');

// contracts
const predictionContract = require('../libs/smartcontract');
const tokenRegistryContract = require('../libs/tokenRegistryContract');
const predictionWithTokenContract = require('../libs/tokenRegistryContract');

const constants = require('../constants');
const utils = require('../libs/utils');
const bl = require('../bl');

const network_id = configs.network_id;
const ownerAddress = configs.network[network_id].ownerAddress;
const amountDefaultValue = configs.network[network_id].amountValue;

let isRunningTask = false;
let taskIdTracking = 0;


const masterRefund = (params) => {
	return new Promise((resolve, reject) => {
		return resolve([{
			contract_method: 'refundMaster',
			hid: params.hid,
			offchain: params.offchain
		}])
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
 * @param {number} params.match_id
 * @param {number} params.outcome_id
 * @param {number} params.side
 * @param {number} params.hid
 * @param {number} params.match_date
 * @param {string} params.match_name
 * @param {string} params.outcome_name
 * @param {number} params.type
 * @param {string} params.amount 
 * @param {address} params.from_address
 * @param {Object} task
 * @param {boolean} isFreeBet
 */
const initBet = (params, task, isFreeBet) => {
	return new Promise(async (resolve, reject) => {
		try {

			if (params.hid == null || params.hid == 'null' || params.hid == undefined) {
				await taskDAO.updateStatusById(task, constants.TASK_STATUS.STATUS_WAITING_ONCHAIN_HID)
				return resolve(undefined);
			}

			let betAmount = amountDefaultValue + ''
			if (params.amount != null) {
				betAmount = params.amount + ''
			}

			const dataRequest = {
				type: params.type || 3,
				extra_data: utils.gennerateExtraData(params.match_date, params.match_name, params.outcome_name),
				match_id: params.match_id,
				outcome_id: params.outcome_id,
				amount: betAmount,
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
				// Save all reponse to Task table
				const tnxs = [];
				(results || []).forEach(item => {
					tnxs.push({
						task_type: task.task_type,
						action: 'INIT_ONCHAIN',
						status: -1,
						contract_address: task.contract_address,
						contract_json: task.contract_json,
						data: JSON.stringify(item),
						date_created: moment().utc().format("YYYY-MM-DD HH:mm:ss"),
						date_modified: moment().utc().format("YYYY-MM-DD HH:mm:ss"),
					});
				});

				taskDAO.multiInsert(tnxs).then((results) => {
					taskDAO.updateStatusById(task, constants.TASK_STATUS.STATUS_SUCCESS);
					return resolve();
				});
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

const initBetOnchain = (params) => {
	return new Promise((resolve, reject) => {
		return resolve([params])
	});
};

/**
 * @param {string} params.offchain
 * @param {number} params.hid
 * @param {number} params.outcome_result
 * @param {string} params.offchain
 */

const resolveReport = (params) => {
	return new Promise((resolve, reject) => {
		return resolve([{
			contract_method: 'resolveOutcomeTransaction',
			hid: params.hid,
			outcome_result: params.outcome_result,
			offchain: params.offchain
		}])
	});
};

/**
 * @param {string} params.offchain
 * @param {number} params.hid
 * @param {number} params.outcome_id
 * @param {number} params.outcome_result
 * @param {string} params.creator_wallet_address
 * @param {number} params.grant_permission
 */

const report = (params) => {
	return new Promise((resolve, reject) => {
		if (params.creator_wallet_address !== null && params.creator_wallet_address !== '' && params.grant_permission == 1) {
			return resolve([{
				contract_method: 'reportOutcomeForCreatorTransaction',
				hid: params.hid,
				outcome_result: params.outcome_result,
				outcome_id: params.outcome_id,
				offchain: params.offchain
			}])

		} else {
			return resolve([{
				contract_method: 'reportOutcomeTransaction',
				hid: params.hid,
				outcome_result: params.outcome_result,
				outcome_id: params.outcome_id,
				offchain: params.offchain
			}])
		}
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
 * @param {string} params.grant_permission
 * @param {string} params.creator_wallet_address
 * @param {number} params.market_fee
 * @param {number} params.id
 * @param {array} params.outcomes
 * @param {number} outcomes.result
 * @param {number} outcomes.public
 * @param {number} outcomes.hid
 * @param {string} outcomes.name
 * 
 */
const createMarket = (params) => {
	return new Promise((resolve, reject) => {
		if (params.date < params.reportTime && params.reportTime < params.disputeTime) {
			return resolve(utils.generateMarkets(params.outcomes, params.grant_permission, params.creator_wallet_address, params.market_fee, params.date, params.disputeTime, params.reportTime, params.source));
		}
		return reject({
			err_type: constants.TASK_STATUS.CREATE_MARKET_TIME_INVALID,
			options_data: { date: params.date, disputeTime: params.disputeTime, reportTime: params.reportTime }
		});
	});
}

/**
 * @param {JSON} hs
 * @param {Object} task
 */
const addFeed = (hs, task) => {
	return new Promise((resolve, reject) => {
		try {
			utils.addFeedAPI(hs)
			.then((result) => {
				taskDAO.updateStatusById(task, constants.TASK_STATUS.STATUS_SUCCESS);
				resolve({});
			})
			.catch(err => {
				console.error(err);
				taskDAO.updateStatusById(task, constants.TASK_STATUS.CALL_SOLR_FAIL);
				resolve({});
			});
		} catch (error) {
			console.log('addFeed error: ', error);
			resolve({});
		}
	});
};

const callSmartContract = (data) => {
	return new Promise((resolve, reject) => {
		utils.getGasAndNonce()
		.then(chain_infor => {
			const gasPriceStr = chain_infor.gasPriceStr;
			const nonce = chain_infor.nonce;
			const tasks = [];
			let index = 0;

			data.forEach(itemData => {
				const onchainData = itemData.onchain_task;
				const task = itemData.task_dao;
				if (onchainData) {
					tasks.push(
						new Promise((resolve, reject) => {
							taskDAO.updateStatusById(task, constants.TASK_STATUS.STATUS_CALL_SMARTCONTRACT_PROGRESSING)
							.then( resultUpdate => {
								let smartContractFunc = null;
								const item = JSON.parse(task.data);
								let arr_tmp = task.contract_json.split('_');
								contract_json = arr_tmp.length > 0 ? arr_tmp[0] : ""

								switch (contract_json) {
									case 'PredictionHandshake':
										switch (onchainData.contract_method) {
											case 'createMarket':
												smartContractFunc = predictionContract.createMarketTransaction(nonce + index, onchainData.fee, onchainData.source, onchainData.closingTime, onchainData.reportTime, onchainData.disputeTime, onchainData.offchain, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
											break;
											case 'createMarketForShurikenUser':
												smartContractFunc = predictionContract.createMarketForShurikenUserTransaction(nonce + index, onchainData.creator_wallet_address, onchainData.fee, onchainData.source, onchainData.grant_permission, onchainData.closingTime, onchainData.reportTime, onchainData.disputeTime, onchainData.offchain, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
											break;
											case 'init':
												smartContractFunc = predictionContract.submitInitTransaction(nonce + index, onchainData.hid, onchainData.side, onchainData.odds, onchainData.offchain, onchainData.amount, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
											break;
											case 'shake':
												smartContractFunc = predictionContract.submitShakeTransaction(onchainData.hid, onchainData.side, onchainData.taker, onchainData.takerOdds, onchainData.maker, onchainData.makerOdds, onchainData.offchain, parseFloat(onchainData.amount), nonce + index, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
											break;
											case 'collectTestDrive':
												smartContractFunc = predictionContract.submitCollectTestDriveTransaction(onchainData.hid, onchainData.winner, onchainData.offchain, nonce + index, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
											break;
											case 'reportOutcomeTransaction':
												smartContractFunc = predictionContract.reportOutcomeTransaction(onchainData.hid, onchainData.outcome_id, onchainData.outcome_result, nonce + index, onchainData.offchain, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
											break;
											case 'reportOutcomeForCreatorTransaction':
												smartContractFunc = predictionContract.reportOutcomeForCreatorTransaction(onchainData.hid, onchainData.outcome_id, onchainData.outcome_result, nonce + index, onchainData.offchain, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
											break;
											case 'initTestDriveTransaction':
												smartContractFunc = predictionContract.submitInitTestDriveTransaction(onchainData.hid, onchainData.side, onchainData.odds, onchainData.maker, onchainData.offchain, parseFloat(onchainData.amount), nonce + index, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
											break;
											case 'shakeTestDriveTransaction':
												smartContractFunc = predictionContract.submitShakeTestDriveTransaction(onchainData.hid, onchainData.side, onchainData.taker, onchainData.takerOdds, onchainData.maker, onchainData.makerOdds, onchainData.offchain, parseFloat(onchainData.amount), nonce + index, gasPriceStr, item,task.contract_address, task.contract_json, task.id);
											break;
											case 'uninitForTrial':
												smartContractFunc = predictionContract.uninitForTrial(onchainData.hid, onchainData.side, onchainData.odds, onchainData.maker, `${onchainData.value}`, onchainData.offchain, nonce + index, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
											break;
											case 'resolveOutcomeTransaction':
												smartContractFunc = predictionContract.resolveOutcomeTransaction(onchainData.hid, onchainData.outcome_result, nonce + index, onchainData.offchain, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
											break;
											case 'refundMaster':
												smartContractFunc = predictionContract.refundMaster(onchainData.hid, onchainData.offchain, nonce + index, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
											break;
										}
									break;
									case 'TokenRegistry': 
										switch (onchainData.contract_method) {
											case 'addNewToken':
												smartContractFunc = tokenRegistryContract.addNewTokenTransaction(nonce + index, onchainData.token_address, onchainData.symbol, onchainData.name, onchainData.decimals, onchainData.offchain, gasPriceStr, item, task.id);
											break;
										}
									break;
									case 'PredictionHandshakeWithToken': 
										switch (onchainData.contract_method) {
											case 'approveNewToken':
												smartContractFunc = predictionWithTokenContract.approveNewToken(nonce + index, onchainData.fee, onchainData.source, onchainData.closingTime, onchainData.reportTime, onchainData.disputeTime, onchainData.offchain, gasPriceStr, item, task.id);
											break;
										}
									break;
								}
	
								if (smartContractFunc) {
									index += 1;
									smartContractFunc.then(result => {
										return resolve(Object.assign(result, { taskId: task.id}));
									}).catch(reject);
								}
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
					console.error('Task onchain is empty with id: ', task.id);
				}
			});

			Promise.all(tasks)
			.then(results => {
				if (Array.isArray(results) && results.length > 0) {
					web3.setNonce( web3.getNonce() + results.length);
					const taskIds = results.map(i => { return i.taskId; })
					return resolve(taskIds);
				} else {
					resolve([]);
				}
			})
			.catch(err => {
				return reject(err);
			})
		})
		.catch(reject);
	});
};

const asyncScanTask = () => {
	return new Promise((resolve, reject) => {
		const tasks = [];
		utils.taskMarkId(taskIdTracking)
		.then(_tasks => {
			taskIdTracking = _tasks.length > 0 ? _tasks[_tasks.length - 1].id : 0;
			_tasks.forEach(task => {
				if (task != undefined) {
					tasks.push(
						new Promise((resolve, reject) => {
							taskDAO.updateStatusById(task, constants.TASK_STATUS.STATUS_PROGRESSING)
							.then( resultUpdate => {
								const params = JSON.parse(task.data)
								let processTaskFunc = undefined;

								switch (task.task_type) {
									case 'NORMAL': // ETHER
										switch (task.action) {
											case 'ADD_FEED':
												processTaskFunc = addFeed(params, task);
											break;
										}
									break;

									case 'REAL_BET': // ETHER
										switch (task.action) {
											case 'INIT':
												processTaskFunc = initBet(params, task, false);
											break;
											case 'INIT_ONCHAIN':
												processTaskFunc = initBetOnchain(params);
											break;
											
											case 'REPORT':
												processTaskFunc = report(params);
											break;
											case 'CREATE_MARKET':
												processTaskFunc = createMarket(params);
											break;
											case 'RESOLVE':
												processTaskFunc = resolveReport(params);
											break;
										}
									break;

									case 'FREE_BET': // ETHER
										switch (task.action) {
											case 'INIT':
												processTaskFunc = initBet(params, task, true);
											break;
											case 'INIT_ONCHAIN':
												processTaskFunc = initBetOnchain(params);
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
										switch (task.action) {
											case 'ADD_TOKEN': {
												processTaskFunc = bl.tokenRegistry.addToken(params);
											}
											break;
										}
									
									case 'MASTER_COLLECT':
										switch (task.action) {
											case 'HANDSHAKE_REFUND': {
												processTaskFunc = masterRefund(params);
											}
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
								.then(results => {
									return resolve({
										task_dao: task,
										onchain_task: results
									});
								})
								.catch(err => {
									utils.handleErrorTask(task, err.err_type);
									return resolve();
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
			.then( results => {
				const onchain_arr = [];
				results.forEach(item => {
					if (item) {
						if (Array.isArray(item.onchain_task)){
							item.onchain_task.forEach(_item => {
								onchain_arr.push({
									task_dao: item.task_dao,
									onchain_task: _item
								});
							});
						} else {
							onchain_arr.push({
								task_dao: item.task_dao,
								onchain_task: item.onchain_task
							});
						}
					}
				});
				return callSmartContract(onchain_arr);
			})
			.then(taskIds => {
				taskDAO.multiUpdateStatusById(taskIds, constants.TASK_STATUS.STATUS_SUCCESS)
				.then(updateResults => {
					return resolve(updateResults);
				})
				.catch(err => {
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

			if (isRunningTask === false) {
				isRunningTask = true;
				
				asyncScanTask()
				.then(results => {
					isRunningTask = false;
				})
				.catch(e => {
					isRunningTask = false;
					console.error(e);
				})

			} 
		} catch (e) {
			isRunningTask = false;
			console.log('cron task error');
			console.error(e);
		}
	});
};

module.exports = { runTaskCron };
