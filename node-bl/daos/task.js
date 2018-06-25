
const models = require('../models');
const constants = require('../constants');

const Op = models.Sequelize.Op;

module.exports = {
    getTasksByStatus: () => {
        return models.Task.findAll({
            where: {
                [Op.or]: [{
                    status: constants.TASK.STATUS_PENDING
                }, {
                    status: constants.TASK.STATUS_RETRY
                }]
            },
            limit: 10
        });
    },
};
