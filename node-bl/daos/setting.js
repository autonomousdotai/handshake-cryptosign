const models = require('../models');

module.exports = {
  getByName: function (name) {
    return models.Setting
        .findOne({
            where: { name: name }
        });
  }
};