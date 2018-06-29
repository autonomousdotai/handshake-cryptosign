
const configs = require('../configs');
const axios = require('axios');
const moment = require('moment');
const web3 = require('../configs/web3').getWeb3();
const handshakeDAO = require('../daos/handshake');

const calulaOdds = (value) => {
    return parseInt(response.data[0].odds  * 100);
}

const gennerateExtraData = (match, outcome) => {
    return JSON.stringify({
        event_name: match.name,
        event_predict: outcome.name,
        date: moment((match.date || 0) * 1000).format("MMM DD")
    });
};

const gennerateOddsArr = (outcomes, isGenSup) => {
    return new Promise((resolve, reject) => {
        var tasks = [];
        (outcomes || []).forEach(outcome => {
            tasks.push(new Promise(async (resolve, reject) => {
                (isGenSup ? gennerateOddsSupport : gennerateOddsAgainst)(outcome.id)
                .then(result => {
                    if (!result) {
                        return resolve(null);
                    }
                    return resolve({
                        odds: result,
                        outcome: outcome,
                        isSup: isGenSup
                    });
                })
                .catch(reject)
            }));
        })
        Promise.all(tasks)
        .then(resolve)
        .catch(reject);
    });
}

const gennerateOddsSupport = (outcomeId) => {
    return new Promise((resolve, reject) => {
        // get max odds of againt by outcomeId
        handshakeDAO.findByOutcomeID(outcomeId, false, true)
        .then(result => {
            if (!result || !result.toJSON() || !result.toJSON().odds || result.toJSON().odds <= 1) {
                return resolve(null);
            }

            return resolve((parseFloat(result.toJSON().odds || 0) + 0.1 * (Math.floor(Math.random() * 9) + 1)).toFixed(2));
        })
        .catch((error) => {
            console.error('DB: random Odds Support err: ', error);
            return reject(error);
        });
    });
}

const gennerateOddsAgainst = (outcomeId) => {
    return new Promise((resolve, reject) => {
        //get min odds of support by outcomeId
        handshakeDAO.findByOutcomeID(outcomeId, true, false)
        .then(result => {
            if (!result || !result.toJSON() || !result.toJSON().odds || result.toJSON().odds <= 1) {
                return resolve(null);
            }
            const minOddSupport = parseFloat(result.toJSON().odds || 0).toFixed(2);
            return resolve(minOddSupport / (minOddSupport - 0.1));
        })
        .catch((error) => {
            console.error('DB: random Odds Support err: ', error);
            return reject(error);
        });
    });
}

const randomOdds = (side) => {
    const oddSupportValue = [2.9, 2.8, 2.7];
    const oddAgainstValue = [1.8, 1.7, 1.6];
    const index = Math.floor((Math.random() * (oddAgainstValue.length - 1)) + 1);
    return (side === 1 ? oddSupportValue : oddAgainstValue)[index];
}

const getNonceFromAPI = (address, length) => {
    return new Promise((resolve, reject) => {
        setTimeout( async () => {
            try {
                const tnxCount = await web3.eth.getTransactionCount(address, 'latest');
                return resolve(tnxCount);
                /*
                
                const path = `address=${address}&network_id=${configs.network_id}`;
                const tnxCount = await web3.eth.getTransactionCount(address, 'latest');

                // Get nonce from API
                axios.get(`https://staging.ninja.org/api/nonce/get?address=${address}&network_id=${configs.network_id}`, {
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

                    // const newNonce = response.data.data.nonce > tnxCount ? tnxCount : response.data.data.nonce;
                    const newNonce = tnxCount;
                    // Set new nonce to API
                    // axios.post(`${configs.restApiEndpoint}/nonce/set?${path}&nonce=${(newNonce + (length || 0))}`, {}, {
                    axios.post(`https://staging.ninja.org/api/nonce/set?${path}&nonce=${(newNonce + (length || 0))}`, {}, {
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
                */
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
const submitInit = (outcome, match, address, side, chainId, amount, odds) => {
    return new Promise((resolve, reject) => {
        const dataRequest = {
            type: 3,
            extra_data: gennerateExtraData(match, outcome),
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

module.exports = {
    submitInit,
    getNonceFromAPI,
    gennerateOddsSupport,
    gennerateOddsAgainst,
    gennerateOddsArr,
    randomOdds,
    gennerateExtraData
};
