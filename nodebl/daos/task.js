
const models = require('../models');
const constants = require('../constants');
const moment = require('moment');

const Op = models.Sequelize.Op;

module.exports = {
    getTasksByStatus: (id) => {
        return models.Task.findAll({
            where: {
                id: {
                    gt: id || 0
                },
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
            status: status,
            date_modified: moment().utc().format("YYYY-MM-DD HH:mm:ss")
        });
    },
    multiUpdateStatusById: (ids, status) => {
        return models.Task.update({
            status: status,
            date_modified: moment().utc().format("YYYY-MM-DD HH:mm:ss")
        }, {
            where: {
                id: ids
            }
        });
    },
    getLastIdByStatus: () => {
        return models.Task.findOne({
            where: {
                [Op.or]: [{
                    status: constants.TASK_STATUS.STATUS_PENDING
                }, {
                    status: constants.TASK_STATUS.STATUS_RETRY
                }]
            },
            order: [
                ['id', 'DESC']
            ],
            attributes: ['id'] 
        });
    },
    multiInsert: (items) => {
        return new Promise((resolve, reject ) => {
          return models.Task.bulkCreate(items, {
            validate: true
          })
          .then(resolve)
          .catch(reject)
        });
      },
};
