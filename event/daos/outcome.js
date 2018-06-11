const models = require('../models');

module.exports = {
    getOutcomesNullHID: function () {
        return models.Outcome
            .findAll({
                where: {
                    hid: null
                }
            });
    },
    updateOutcomeHID: function (outcome, hid) {
        return outcome
            .update({
                hid: hid
            });
    }
};
