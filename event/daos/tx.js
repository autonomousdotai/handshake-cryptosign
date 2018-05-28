const models = require('../models');
const constants = require('../constants');

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
};
