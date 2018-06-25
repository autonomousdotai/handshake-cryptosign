const models = require('../models');
const constants = require('../constants');

module.exports = {
  getByBlock: function (address, block, log_index) {
    return models.Event
        .findOne({
            order: [
                ['id', 'DESC']],
            where: {
                address: address,
                block: block,
                log_index: log_index,
            }
        });
  },
  getLastLogByName: function (address, event_name) {
      return models.Event
          .findOne({
              order: [
                  ['id', 'DESC']],
              where: {
                  address: address,
                  event_name: event_name,
              }
          });
  },
  getAllLog: function () {
      return models.Event
          .findAll({
              where: {
                  event_name: 'CLICK_BUTTON'
              }
          });
  },
  create: function (tx, address, event_name, value, block, log_index) {
      return models.Event
          .create(
          {
              address: address,
              event_name: event_name,
              value: value,
              block: block,
              log_index: log_index,
              date_created: new Date(),
          }, {transaction: tx}
      )
  }
};
