
const cron = require('node-cron');
const handshakeDAO = require('../daos/handshake');
const settingDAO = require('../daos/setting');
const taskDAO = require('../daos/task');
const outcomeDAO = require('../daos/outcome');

let isRunningCollectTask = false;

const asyncScanTask = (fromId) => {
	return new Promise((resolve, reject) => {

		handshakeDAO.getAllMasterCollect(fromId)
		.then(items => {
			const tnxs = [];
			if (!items || items.length == 0) {
				return resolve();
			}
			
			tasks = [];
			items.forEach(hs => {
				tasks.push(
					new Promise((resolve, reject) => {
						outcomeDAO.getById(hs.outcome_id)
						.then(outcome => {
							if (outcome.hid >= 0) {
								tnxs.push({
									task_type: 'MASTER_COLLECT',
									data: JSON.stringify({
										contract_method: 'uninitForTrial',
										hid: outcome.hid,
										side: hs.side,
										odds: parseInt(hs.odds * 100),
										maker: hs.from_address, // owner address
										value: hs.amount,
										offchain: `cryptosign_m${hs.id}`
									}),
									action: 'HANDSHAKE_UNINIT',
									status: -1,
									contract_address: hs.contract_address,
									contract_json: hs.contract_json
								});
							}
							resolve();
						})
						.catch(reject)
					})
				);
			});
			Promise.all(tasks)
			.then(results => {
				taskDAO.multiInsert(tnxs).then((results) => {
					const hs_ids = items.map(i => { return i.id; })
	
					handshakeDAO.multiUpdateStatusById(hs_ids, -4) // 'STATUS_MAKER_UNINIT_PENDING': -4,
					.then(updateResults => {
						return resolve(updateResults);
					})
					.catch(err => {
						console.error('Error update onchain task status: ', err);
						return reject(err);
					})
	
				}).catch(reject);
			})
			.catch(reject);
		})
		.catch(reject)
	})
};

const runCron = () => {
    cron.schedule('*/15 * * * * *', async () => {
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
