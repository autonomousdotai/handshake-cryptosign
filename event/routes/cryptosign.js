const express = require('express');
const router  = express.Router();
const configs = require('../configs');
const predictionContract = require('../libs/smartcontract');
const scriptInitHandshake = require('../libs/scriptHandshake');
const network_id = configs.network_id;
const ownerAddress = configs.network[network_id].ownerAddress;

router.post('/init', async function(req, res, next) {
    try {
        const arrObject = req.body || [];

        if (!Array.isArray(arrObject) || arrObject.length == 0) {
            console.log('POST: init data invalid');
            return next();
        }

        const tasks = []
        const nonce = await predictionContract.getNonce(ownerAddress);

        arrObject.forEach((requestObject, index) => {
            tasks.push(new Promise((resolve, reject) => {
                const hid = parseInt(requestObject.hid);
                const side = parseInt(requestObject.side);
                const odds = parseInt(requestObject.odds); // TODO: check is float or * 100
                const address = requestObject.address;
                const offchain = requestObject.offchain;    
                let fncSubmitTnx = null;

                if (offchain) {
                    if (offchain.indexOf('_m') != -1) {
                        fncSubmitTnx = predictionContract.submitInitTestDriveTransaction(hid, side, odds, address, offchain, nonce + index);
                    } else if (offchain.indexOf('_s') != -1) {
                        // TODO: check params
                        fncSubmitTnx = predictionContract.submitShakeTestDriveTransaction(hid, side, odds, address, offchain, nonce + index);
                    } else {
                        console.error('offchain invalid: ', offchain);
                        return resolve();
                    }
                    fncSubmitTnx
                    .then(result => {
                        console.log(result);
                        resolve();
                    })
                    .catch(err => {
                        console.error(err);
                        reject(err);
                    });
                }
                // cryptosign_m14 // initTestDrive
                // cryptosign_s14 // shakeTestDrive
            }));
        });

        Promise.all(tasks)
        .then(result => {
            res.ok('Init done.');
        })
        .catch(err => {
            return next (err);
        })
    } catch (err) {
        console.log('route init throw exception');
        next(err);
    }
});

router.post('/shake', async function(req, res, next) {
    try {
        const requestObject = req.body;
        const hid = parseInt(requestObject.hid);
        const side = parseInt(requestObject.side);
        const odds = parseInt(requestObject.odds);
        const address = requestObject.address;
        const offchain = requestObject.offchain;

        predictionContract.submitInitTestDriveTransaction(hid, side, odds, address, offchain)
                            .then((hash) => {
                                console.log(`Init test drive ${offchain} success, hash: ${hash}`);
                                res.ok(hash);
                            })
                            .catch((e) => {
                                console.log(`Init test drive ${offchain} fail, ${e.message}`);
                                res.notok(e.message);
                            });

    } catch (err) {
        console.log('route init throw exception');
        next(err);
    }
});

router.post('/odds/init', (req, res, next) => {
    try {
        const start = parseInt(req.query.start);
        const end = parseInt(req.query.end);
        const outcome_data = req.body;

        if (start >= end || start == null || start == undefined || end == null || end == undefined) {    
            console.log(' start or end value is invalid');
            res.ok('Init odds data false.');
            return next();
        }
        if (!Array.isArray(outcome_data)) {
            console.log('Init odds false: body invalid.');
            res.ok('Init odds false: body invalid.');
            return next();
        }
        scriptInitHandshake.initHandshake(start, end, outcome_data);
        res.ok('Init odds data.');
    } catch (err) {
        next(err);
    }
});

router.post('/report', (req, res, next) => {
    try {
        if (!req.body || req.body.hid == undefined || req.body.outcome_result == undefined) {
            console.error(' Report outcome tnx invalid ');
            return next();
        }
        predictionContract.reportOutcomeTransaction(req.body.hid, req.body.outcome_result)
        .catch(console.error);
        res.ok('Report outcome.');
    } catch (err) {
        next(err);
    }
});

module.exports = router;