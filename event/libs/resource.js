
const configs = require('../configs');
const axios = require('axios');
const moment = require('moment');
const outcomeDAO = require('../daos/handshake');
const web3 = require('../configs/web3').getWeb3();

const randomOddsSupport = async (match) => {
    const maxOddSupport = await outcomeDAO.findOddByMatchID(match.id, true);

}

const randomOddsAgainst = async (match) => {
    const minOddAgainst = await outcomeDAO.findOddByMatchID(match.id, true);
    const minOddSupport = await outcomeDAO.findOddByMatchID(match.id, false);

}

const getNonceFromAPI = (address, length) => {
    return new Promise((resolve, reject) => {
        setTimeout( async () => {
            try {
                const path = `address=${address}&network_id=${configs.network_id}`;
                const tnxCount = await web3.eth.getTransactionCount(address, 'latest');

                // Get nonce from API
                axios.get(`https://stag-handshake.autonomous.ai/api/nonce/get?address=${address}&network_id=${configs.network_id}`, {
                // axios.get(`${configs.restApiEndpoint}/nonce/get?address=${address}&network_id=${configs.network_id}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Payload': 'Rz_oUgtEt0hJbcFzD_OEaePbzjDKH_aP484G6USgcmlRVD_NXk1DfmYgIQ=='
                    }
                })
                .then(response => {
                    if (!response.data || response.data.status !== 1) {
                        console.error('Cannot get Nonce.');
                        return resolve(tnxCount);
                    }

                    const newNonce = response.data.data.nonce > tnxCount ? tnxCount : response.data.data.nonce;
                    // Set new nonce to API
                    // axios.post(`${configs.restApiEndpoint}/nonce/set?${path}&nonce=${(newNonce + (length || 0))}`, {}, {
                    axios.post(`https://stag-handshake.autonomous.ai/api/nonce/set?${path}&nonce=${(newNonce + (length || 0))}`, {}, {
                        headers: {
                            'Content-Type': 'application/json',
                            'Payload': 'Rz_oUgtEt0hJbcFzD_OEaePbzjDKH_aP484G6USgcmlRVD_NXk1DfmYgIQ=='
                        }
                    })
                    .then(response => {
                        if (!response.data || response.data.status !== 1) {
                            return reject('Cannot set Nonce.');
                        }
                        return resolve(newNonce);
                    })
                    .catch(e => {
                        console.error(e);
                        return reject(e);
                    });
                })
                .catch(e => {
                    console.error(e);
                    return reject(e);
                });
            } catch (e) {
                console.error('Get nonce err: ', e);
                reject(e);
            }
        }, 20000);
    });
};

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
                'UID': configs.uid,
                'Fcm-Token': configs.fcm_token
            }
        })
        .then((response) => {
            return resolve(response.data);
        })
        .catch((error) => {
            return reject(error);
        });
    });
};

module.exports = { submitInit, getNonceFromAPI };
