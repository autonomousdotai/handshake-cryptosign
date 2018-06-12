const express = require('express');
const router  = express.Router();
const configs = require('../configs');


router.post('/init', async function(req, res, next) {
    try {
        const requestObject = req.body;
        const address = requestObject.address;
        const privateKey = requestObject.privateKey;
        const value = requestObject.value;
        const term = parseInt(requestObject.term);
        const deliveryDate = requestObject.delivery_date;
        const toAddress = requestObject.to_address;
        const offchain = requestObject.offchain;

        const neuronInstanceName = terms[term] || 'basicHandshake';
        const handshakeInstance = neuron[neuronInstanceName];
        
        let result = {};
        if (term === PAYABLE_HANDSHAKE_TERM) {
            console.log('case payable handshake');
            const method = 'init';
            if (!handshakeInstance[method]) {
            res.notok(new Error('Unknown ' + method + ' for your handshake'));
            }
            result = await handshakeInstance[method](address, privateKey, toAddress, value, deliveryDate, offchain);
            // save info to result
            result['contractName'] = handshakeInstance.constructor.name;
            result['contractAddress'] = handshakeInstance.instance.options.address;
            result['contractMethod'] = method;
        } else {
            const method = 'init';
            if (!handshakeInstance[method]) {
            res.notok(new Error('Unknown ' + method + ' for your handshake'));
            }
            result = await handshakeInstance[method](address, privateKey, toAddress, offchain);
            // save info to result
            result['contractName'] = handshakeInstance.constructor.name;
            result['contractAddress'] = handshakeInstance.instance.options.address;
            result['contractMethod'] = method;
        }
    
        res.ok(result);
    } catch (err) {
        console.log('route init throw exception');
        next(err);
    }
});

module.exports = router;