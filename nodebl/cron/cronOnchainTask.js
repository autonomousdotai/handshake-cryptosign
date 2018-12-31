
const cron = require('node-cron');
const web3 = require('../configs/web3');

// daos
const onchainTaskDAO = require('../daos/onchainTask');
const settingDAO = require('../daos/setting');

const constants = require('../constants');
const utils = require('../libs/utils');

// contracts
const predictionContract = require('../libs/smartcontract');
const tokenRegistryContract = require('../libs/tokenRegistryContract');
const predictionWithTokenContract = require('../libs/tokenRegistryContract');

let isRunningOnchainTask = false;

const asyncScanOnchainTask = () => {
	return new Promise((resolve, reject) => {
		utils.getGasAndNonce()
		.then(result => {
			const gasPriceStr = result.gasPriceStr;
			const nonce = result.nonce;
			const tasks = [];
			let index = 0;
			onchainTaskDAO.getOnchainTasksByStatus()
			.then(_tasks => {
				_tasks.forEach(task => {
					if (task && task.data) {
						tasks.push(
							new Promise((resolve, reject) => {
								onchainTaskDAO.updateStatusById(task, constants.TASK_STATUS.STATUS_PROGRESSING)
								.then( resultUpdate => {
									let smartContractFunc = null;
									const item = JSON.parse(task.data);
									const onchainData = item.onchainData;
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
												case 'uninitMaster':
													smartContractFunc = predictionContract.uninitMaster(onchainData.hid, onchainData.side, onchainData.odds, `${onchainData.value}`, onchainData.offchain, nonce + index, gasPriceStr, item, task.contract_address, task.contract_json, task.id);
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
											return resolve(Object.assign(result, { onchainTaskId: task.id}));
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
						console.error('Task is empty with id: ', task.id);
					}
				});

				Promise.all(tasks)
				.then(results => {
					if (Array.isArray(results) && results.length > 0) {
						web3.setNonce( web3.getNonce() + results.length);
						const taskIds = results.map(i => { return i.onchainTaskId; })

						onchainTaskDAO.multiUpdateStatusById(taskIds, constants.TASK_STATUS.STATUS_SUCCESS)
						.then(updateResults => {
							return resolve(results);
						})
						.catch(err => {
							console.error('Error update onchain task status: ', err);
							return reject(err);
						})
					} else {
						resolve([]);
					}
				})
				.catch(err => {
					return reject(err);
				})
			})
			.catch(reject);	
		})
		.catch(reject);
	});
};

const runOnchainTaskCron = () => {
    cron.schedule('*/5 * * * * *', async () => {
		try {
			const setting = await settingDAO.getByName('OnchainCronJob');
				if (!setting) {
					console.log('OnchainCronJob setting is null. Exit!');
					return;
				}
				if(!setting.status) {
					console.log('Exit OnchainCronJob setting with status: ' + setting.status);
					return;
				}

			if (isRunningOnchainTask === false) {
				isRunningOnchainTask = true;
				
				asyncScanOnchainTask()
				.then(results => {
					isRunningOnchainTask = false;
				})
				.catch(e => {
					isRunningOnchainTask = false;
					console.error(e);
				})

			} 
		} catch (e) {
			isRunningOnchainTask = false;
			console.log('Onchain cron task error');
			console.error(e);
		}
	});
};

module.exports = { runOnchainTaskCron };
