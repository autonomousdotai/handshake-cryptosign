const models = require('../models');

// side: 0 (unknown), 1 (support), 2 (against)
module.exports = {
    getAgainstOddsNull: function () {
        return models.sequelize.query(
            `SELECT outcome.* FROM outcome WHERE outcome.hid IS NOT NULL AND outcome.deleted = 0 AND NOT EXISTS(SELECT * FROM handshake WHERE handshake.outcome_id = outcome.id AND handshake.side = 2 AND handshake.remaining_amount > 0 AND handshake.deleted = 0) LIMIT 10`,
            { type: models.sequelize.QueryTypes.SELECT, raw: true }
        );
    },
    getSupportOddsNull: function () {
        return models.sequelize.query(
            `SELECT outcome.* FROM outcome WHERE outcome.hid IS NOT NULL AND outcome.deleted = 0 AND NOT EXISTS(SELECT * FROM handshake WHERE handshake.outcome_id = outcome.id AND handshake.side = 1 AND handshake.remaining_amount > 0  AND handshake.deleted = 0) LIMIT 10`,
            { type: models.sequelize.QueryTypes.SELECT, raw: true }
        );
    },
    getOddsNull: function () { // get outcome has support and against null
        return models.sequelize.query(
            `SELECT o.* FROM outcome o LEFT JOIN handshake h ON h.outcome_id = o.id WHERE h.status IS NULL LIMIT 10`,
            { type: models.sequelize.QueryTypes.SELECT, raw: true }
        );
    },
    findByOutcomeID: function (outcome_id, idSupport, isDesc) {
        return models.Handshake
            .findOne({
                order: [
                    ['odds', isDesc ? 'DESC' : 'ASC']],
                where: {
                    outcome_id: outcome_id,
                    side: idSupport ? 1 : 2,
                    deleted: 0
                }
            });
    }
};
