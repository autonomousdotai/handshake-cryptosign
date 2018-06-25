
const cron = require('node-cron');
const configs = require('../configs');

// models
const models = require('../models');

// daos
const taskDAO = require('../daos/task');
const settingDAO = require('../daos/setting');

const web3 = require('../configs/web3').getWeb3();

const bettingHandshakeAddress = configs.network[configs.network_id].bettingHandshakeAddress;

let isRunningTask = false;

const init = () => {

};

const unInit = () => {

};

const collect = () => {

};

const asyncScanTask = () => {
	const tasks = [];
	taskDAO.getTasksByStatus()
	.then(_tasks => {
		_tasks.forEach(task => {
			tasks.push(
				new Promise((resolve, reject) => {
					
					if (!task || !task.task_type) {
						return reject('Task is empty');
					}
					
					let processTaskFunc = undefined;

					switch(task.task_type){
						case 'INIT':
							processTaskFunc = init();
						break;
						case 'UNINIT':
							processTaskFunc = unInit();
						break;
						case 'COLLECT':
							processTaskFunc = collect();
						break;
					}

					processTaskFunc
					.then(result => {
						
					})
					.catch(err => {
						return reject(err);
					})
				})
			)
		})
	})
};

const runTaskCron = () => {
    cron.schedule('*/3 * * * * *', async () => {
		console.log('task cron running a task every 3s at ' + new Date());
		try {
			const setting = await settingDAO.getByName('TaskCronJob');
            if (!setting) {
                console.log('TaskCronJob is null. Exit!');
                return;
            }
            if(!setting.status) {
                console.log('Exit TaskCronJob with status: ' + setting.status);
                return;
            }
            console.log('Begin run TaskCronJob!');

			if (isRunningTask === false) {
					isRunningTask = true;
					
					asyncScanTask().then(result => {
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
