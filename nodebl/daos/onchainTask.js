const models = require('../models');
const constants = require('../constants');
const Op = models.Sequelize.Op;

module.exports = {
  create: (isErc20, contract_address, contract_name, contract_method, from_address, data, status, task_id, description) => {
    return new Promise((resolve, reject ) => {
      models.sequelize.transaction({}, (tx) => {
        return models.OnchainTask
        .create(
        {
            description: description,
            is_erc20: isErc20,
            contract_address: contract_address,
            contract_name: contract_name,
            contract_method: contract_method,
            from_address: from_address,
            data: data,
            status: status,
            task_id: task_id,
            deleted: 0,
            date_created: new Date(),
            date_modified: new Date()
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
  getOnchainTasksByStatus: () => {
    return models.OnchainTask.findAll({
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
  },
  multiUpdateStatusById: (ids, status) => {
    return models.OnchainTask.update({
      status: status
    }, {
      where: {
        id: ids
      }
    });
  }
};
