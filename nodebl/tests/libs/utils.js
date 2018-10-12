
// const sinon = require('sinon');
const models = require('../../models');
const utils = require('../../libs/utils');
const assert = require('assert');

const generateTasks = () => {
    return new Promise((resolve, reject) => {
        tasks = []
        for(let i = 0; i < 22; i++) {
            tasks.push({
                status: -1,
                action: 'INIT',
                task_type: 'REAL_BET'
            });
        }
        models.Task.bulkCreate(tasks, {returning: true})
        .then(results => {
            return resolve(results);
        })
        .catch(e => {
            throw(e);
        })
    });
};

const generateHs = async() => {
    try {
        let tmp = undefined;
        tmp = await models.Handshake.create({
            description: '1',
            user_id: 88,
            outcome_id: 88,
            contract_address: 1,
            deleted: 0,
            status: 100
        });
        return Promise.resolve(tmp);
    } catch (e) {
        return Promise.reject(e);
    }
    
};

const removeAllTaskByIds = async(fromId, toId) => {
    return models.Task.destroy({
        where: {
            id: {
                gte: fromId,
                lte: toId
            },
        }
    })
};

/* Begin test case */
describe('test libs/utils', async() => {
    it('taskMarkId function', async() => {
        // Generate data
        const results = await generateTasks();
        const ids = (results || []).map(e => { return e.id; });

        const tasksResult = await utils.taskMarkId(ids[0]);

        // Clear data
        await removeAllTaskByIds(ids[0], ids[ids.length -1]);

        assert.equal(tasksResult.length, 10);
    });

    it('addFeedAPI function', async() => {
        const hs = await generateHs();
        
        // Make sure Solr-Services started
        const result = await utils.addFeedAPI(hs);

        assert.equal(Object.keys(result).length, 0);
    });
});
