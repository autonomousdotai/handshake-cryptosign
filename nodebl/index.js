
const cron = require('./cron');

cron.taskCron.runTaskCron();
cron.onchainTaskCron.runOnchainTaskCron();
cron.masterCollectCron.runCron();