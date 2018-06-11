
const configs = require('../configs');
const httpRequest = require('../libs/http');
/*
 @oddData: outcome model
*/
/*
{"id":3,"date_created":null,"date_modified":null,"deleted":0,"name":"Spain wins","match_id":5,"hid":2,"result":-1,"tx":null,"modified_user_id":null,"created_user_id":null}
*/
const submitInit = (outcome, match, address, side, chainId, amount) => {
    return new Promise((resolve, reject) => {
        const oddSupportValue = [2.9, 2.8, 2.7];
        const oddAgainstValue = [1.8, 1.7, 1.6];
        const index = Math.floor((Math.random() * (oddAgainstValue.length - 1)) + 1);
        const odds = (side === 1 ? oddSupportValue : oddAgainstValue)[index];

        const dataRequest = {
            type: 3,
            extra_data: `{"event_name":"${match.name}","event_predict":"${outcome.name}"}`,
            description: 'cron job',
            outcome_id: outcome.id,
            odds: odds,
            amount: amount,
            currency: 'ETH',
            chain_id: chainId,
            side: side,
            from_address: address
        };
    
        const options = {
            hostname: configs.env === 'default' ? 'ninja.org' : configs.restApiEndpoint,
            path: `${configs.env === 'default' ? '/api' : '' }/cryptosign/handshake/init`,
            method: 'POST',
            isHttps: true,
            headers: {
              'Content-Type': 'application/json',
              'Payload': configs.payload
            },
            data: dataRequest
        };
        httpRequest.request(options).then(result => {
            return resolve(result);
        }).catch(err => {
            console.log(err);
            return reject(err);
        });
    });
};

module.exports = { submitInit };
