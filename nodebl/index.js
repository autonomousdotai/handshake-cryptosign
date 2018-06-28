
const configs = require('./configs');
const cron = require('./cron');
console.log(configs);
cron.taskCron.runTaskCron();
