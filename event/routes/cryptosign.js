const express = require('express');
const router  = express.Router();
const configs = require('../configs');
const predictionContract = require('../libs/smartcontract');
const scriptInitHandshake = require('../libs/scriptHandshake');

router.post('/init', async function(req, res, next) {
    try {
        const requestObject = req.body;
        const hid = parseInt(requestObject.hid);
        const side = parseInt(requestObject.side);
        const odds = parseInt(requestObject.odds);
        const address = requestObject.address;
        const offchain = requestObject.offchain;

        console.log('[DEBUG] --> ', offchain)

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
        scriptInitHandshake.initHandshake();
        res.ok('Init odds data.');
    } catch (err) {
        next(err);
    }
});

module.exports = router;