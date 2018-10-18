const models = require('../models');
const constants = require('../constants');
const moment = require('moment');
const Op = models.Sequelize.Op;

module.exports = {
  create: (contract_address, contract_json, contract_method, from_address, data, status, task_id) => {
    return new Promise((resolve, reject ) => {
      models.sequelize.transaction({}, (tx) => {
        return models.OnchainTask
        .create(
        {
            contract_address: contract_address,
            contract_json: contract_json,
            contract_method: contract_method,
            from_address: from_address,
            data: data,
            status: status,
            task_id: task_id,
            deleted: 0,
            date_created: moment().utc().format("YYYY-MM-DD HH:mm:ss"),
            date_modified: moment().utc().format("YYYY-MM-DD HH:mm:ss")
        }, {
          transaction: tx
        })
        .then(resolve)
        .catch(reject)
      });
    });
  },
  multiInsert: (items) => {
    return new Promise((resolve, reject ) => {
      return models.OnchainTask.bulkCreate(items, {
        validate: true
      })
      .then(resolve)
      .catch(reject)
    });
  },
  getOnchainTasksByStatus: (id) => {
    return models.OnchainTask.findAll({
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
    return models.OnchainTask.update({
      status: status,
      date_modified: moment().utc().format("YYYY-MM-DD HH:mm:ss")
    }, {
      where: {
        id: ids
      }
    });
  },
  getLastIdByStatus: () => {
      return models.OnchainTask.findOne({
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
  }
};
