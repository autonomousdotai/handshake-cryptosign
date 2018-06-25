
const configs = require('./configs');
const cron = require('./cron');

setTimeout( () => {
    cron.bettingCron.runBettingCron();
}, 1)
