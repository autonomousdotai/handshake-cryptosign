const models = require('../models');
const constants = require('../constants');
const moment = require('moment');

module.exports = {
  getAllPending: function () {
    return models.Tx.findAll({
      order: [
        ['date_created', 'DESC']],
      where: {
        status: constants.Tx.STATUS_PENDING,
      }
    });
  },
  create: function (hash, contract_address, contract_method, status, chain_id, offchain, payload) {
    return new Promise((resolve, reject ) => {
      models.sequelize.transaction({}, (tx) => {
        return models.Tx
        .create(
        {
            hash: hash,
            contract_address: contract_address,
            contract_method: contract_method,
            status: status,
            chain_id: chain_id,
            offchain: offchain,
            payload: payload,
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
  }
};
