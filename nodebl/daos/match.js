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
    }
};
