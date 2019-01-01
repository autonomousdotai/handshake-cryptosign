
const cron = require('node-cron');
const handshakeDAO = require('../daos/handshake');
const outcomeDAO = require('../daos/outcome');
const settingDAO = require('../daos/setting');
const taskDAO = require('../daos/task');

let isRunningCollectTask = false;

const asyncScanTask = (fromId) => {
	return new Promise((resolve, reject) => {

		outcomeDAO.getAllMasterCollect()
		.then(outcomes => {
			const tnxs = [];
			if (!outcomes || outcomes.length == 0) {
				return resolve();
			}
			const tasks = [];
			const hs_update_id = [];
			const oc_update_ids = [];

			outcomes.forEach(outcome => {
				tasks.push(
					new Promise((resolve, reject) => {
						handshakeDAO.getFirstMasterCollect(outcome.id)
						.then(handshake => {
							if (handshake) {
								tnxs.push({
									task_type: 'MASTER_COLLECT',
									data: JSON.stringify({
										contract_method: 'refundMaster',
										hid: handshake.Outcome.hid,
										offchain: `cryptosign_m${handshake.id}`
									}),
									action: 'HANDSHAKE_REFUND',
									status: -1,
									contract_address: handshake.contract_address,
									contract_json: handshake.contract_json,
								});
								hs_update_id.push(handshake.id);
							}
							resolve();
						})
						.catch(err => {
							console.error('Error get outcome: ', err);
							return reject(err);
						})
					})
				);
				oc_update_ids.push(outcome.id);
			});

			Promise.all(tasks)
			.then(results => {
				const all_oc_ids = outcomes.map(i => { return i.id; })
				outcomeDAO.multiUpdateOutcomeMasterStatus(all_oc_ids, "scanned")
				.then(result => {
					taskDAO.multiInsert(tnxs).then((results) => {
						outcomeDAO.multiUpdateOutcomeMasterStatus(oc_update_ids, "collect")
						.then(resultOcUpdate => {
							handshakeDAO.multiUpdateStatusById(hs_update_id, -4) // 'STATUS_MAKER_UNINIT_PENDING': -4,
							.then(updateResults => {
								return resolve(updateResults);
							})
							.catch(err => {
								console.error('Error update handshake status: ', err);
								return reject(err);
							})	
						})
						.catch(err => {
							console.error('Error update outcome status: ', err);
							return reject(err);
						})
					})
					.catch(err => {
						return reject(err);
					})
				}).catch(reject);
			}).catch(reject);
		})
		.catch(reject)
	})
};

const runCron = () => {
    cron.schedule('* */5 * * * *', async () => {
		try {
			const setting = await settingDAO.getByName('MasterCollect');
				if (!setting) {
					console.log('MasterCollect setting is null. Exit!');
					return;
				}
				if(!setting.status) {
					console.log('Exit MasterCollect setting with status: ' + setting.status);
					return;
				}

			if (isRunningCollectTask === false) {
				isRunningCollectTask = true;
				
				asyncScanTask(setting.value || 0)
				.then(results => {
					isRunningCollectTask = false;
				})
				.catch(e => {
					isRunningCollectTask = false;
					console.error(e);
				})

			} 
		} catch (e) {
			isRunningCollectTask = false;
			console.log('cron task error');
			console.error(e);
		}
	});
};

module.exports = { runCron };
