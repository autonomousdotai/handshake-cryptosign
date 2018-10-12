
const sinon = require('sinon');
const hsDao = require('../../daos/handshake');
const models = require('../../models');
// const assert = require('assert');
// const expect = require('chai').expect;


let sandbox;
/* Before Earch */
beforeEach( () => {
    sandbox = sinon.createSandbox();
});

/* After Earch */
afterEach( () => {
    sandbox.restore();
});


/* Begin test case */

const addNewHandShake = async(data) => {
    return models.Handshake.create(data);
}

describe('handshake DAO', async() => {
    it('getById', async() => {
        const newHS = await addNewHandShake({
            user_id: 88,
            outcome_id: 88,
            contract_address: 1,
            deleted: 0
        });
        const hs = await hsDao.getById(newHS.id);
        const spy = sinon.spy();
        spy(hs);
        sinon.assert.calledWith(spy, sinon.match({ outcome_id: 88 }));
        sinon.assert.calledWith(spy, sinon.match({ user_id: 88, outcome_id: 88 }));
        sinon.assert.calledWith(spy, sinon.match.has("user_id", 88));
    });

});
