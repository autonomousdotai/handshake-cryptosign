
const configs = require('../configs');
const axios = require('axios');
const moment = require('moment');
const outcomeDAO = require('../daos/outcome');


const randomOddsSupport = async (match) => {
    const maxOddSupport = await outcomeDAO.findOddByMatchID(match.id, true);

}

const randomOddsAgainst = async (match) => {
    const minOddAgainst = await outcomeDAO.findOddByMatchID(match.id, true);
    const minOddSupport = await outcomeDAO.findOddByMatchID(match.id, false);

}

/*
 @oddData: outcome model
*/
const submitInit = (outcome, match, address, side, chainId, amount) => {
    return new Promise((resolve, reject) => {
        const oddSupportValue = [2.9, 2.8, 2.7];
        const oddAgainstValue = [1.8, 1.7, 1.6];
        const index = Math.floor((Math.random() * (oddAgainstValue.length - 1)) + 1);
        const odds = (side === 1 ? oddSupportValue : oddAgainstValue)[index];

        if (side === 1) { // support
            
        } else { // against
            
        }

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

        axios.post(`${configs.restApiEndpoint}/handshake/init`, dataRequest, {
            headers: {
                'Content-Type': 'application/json',
                'Payload': configs.payload,
                'UID': `${+moment.utc()}`,
                'FCM_TOKEN': ''
            },
        })
        .then((response) => {
            return resolve(response.data);
        })
        .catch((error) => {
            return reject(error);
        });
    });
};

module.exports = { submitInit };
