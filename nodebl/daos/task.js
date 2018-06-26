
const models = require('../models');
const constants = require('../constants');

const Op = models.Sequelize.Op;

module.exports = {
    getTasksByStatus: () => {
        return models.Task.findAll({
            where: {
                [Op.or]: [{
                    status: constants.TASK_STATUS.STATUS_PENDING
                }, {
                    status: constants.TASK_STATUS.STATUS_RETRY
                }]
            },
            limit: 10
        });
    },
    updateStatusById: (task, status) => {
        return task.update({
            status: status
        });
    }
};
