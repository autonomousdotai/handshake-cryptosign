const express = require('express');
const router  = express.Router();
const predictionContract = require('../libs/smartcontract');
const scriptInitHandshake = require('../libs/scriptHandshake');

router.post('/init', async function(req, res, next) {
    try {
        const arrObject = req.body;

        arrObject.forEach(requestObject => {
            const hid = parseInt(requestObject.hid);
            const side = parseInt(requestObject.side);
            const odds = parseInt(requestObject.odds);
            const address = requestObject.address;
            const offchain = requestObject.offchain;    

            cryptosign_m14 // initTestDrive
            cryptosign_s14 // shakeTestDrive
        });

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