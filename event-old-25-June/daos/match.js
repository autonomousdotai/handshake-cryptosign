const models = require('../models');

module.exports = {
    getAll: function () {
        return models.Match.findAll({});
    },
    getMatchById: function (match_id) {
        return models.Match
        .findOne({
            where: {
                id: match_id,
                deleted: 0
            }
        });
    },
    getMatchByName: function (name) {
        return models.Match
        .findOne({
            where: {
                name: name,
                deleted: 0
            }
        });
    },
    scriptUpdateTime: function (match, reportTime, disputeTime) {
        return match
            .update({
                reportTime,
                disputeTime
            });
    }
};
