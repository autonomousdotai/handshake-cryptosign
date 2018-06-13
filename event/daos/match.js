const models = require('../models');

module.exports = {
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
    }
};
