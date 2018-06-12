
// const cron = require('./cron');
// cron.bettingCron.runBettingCron();
// // cron.oddsCron.runOddsCron();
// cron.createMarketCron.runCreateMarketCron();


const axios = require('axios');
axios.get(`https://stag-handshake.autonomous.ai/api/nonce/get?address=0xea5baf7008cda0e970f91b01f52f4216696c8fc3&network_id=4`, {
                // axios.get(`${configs.restApiEndpoint}/nonce/get?address=${address}&network_id=${configs.network_id}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Payload': 'Rz_oUgtEt0hJbcFzD_OEaePbzjDKH_aP484G6USgcmlRVD_NXk1DfmYgIQ=='
                    },
                    
                })
                .then(console.log)
                .catch(console.error)