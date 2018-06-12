const models = require('../models');

// side: 0 (unknown), 1 (support), 2 (against)
module.exports = {
    getOutcomesNullHID: function () {
        return models.Outcome
            .findAll({
                where: {
                    hid: null
                },
                limit: 20
            });
    },
    updateOutcomeHID: function (outcome, hid) {
        return outcome
            .update({
                hid: hid
            });
    }
};
