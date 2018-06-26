const models = require('../models');

// side: 0 (unknown), 1 (support), 2 (against)
module.exports = {
    getById: function (id) {
        return models.Outcome.findOne({
            where: {
                id: id
            }
        });
    },
    getByMatchId: function (matchId) {
        return models.Outcome.findOne({
            where: {
                match_id: matchId
            }
        });
    },
    getAll: function () {
        return models.Outcome.findAll({});
    },
    getOutcomesNullHID: function () {
        return models.Outcome
            .findAll({
                where: {
                    deleted: 0,
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
