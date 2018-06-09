const models = require('../models');

module.exports = {
    getOutcomesNullHID: function () {
        return models.Outcome
            .findAll({
                where: {
                    hid: null
                }
            });
    }
};
