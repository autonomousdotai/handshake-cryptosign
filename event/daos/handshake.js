const models = require('../models');

// side: 0 (unknown), 1 (support), 2 (against)
module.exports = {
    getAgainstOddsNull: function () {
      return models.sequelize.query(
        `SELECT outcome.* FROM outcome WHERE outcome.hid != -1 AND NOT EXISTS(SELECT * FROM handshake WHERE handshake.outcome_id = outcome.id AND handshake.side = 2 AND handshake.remaining_amount > 0) LIMIT 20`,
        { type: models.sequelize.QueryTypes.SELECT, raw: true }
      );
    },
    getSupportOddsNull: function () {
      return models.sequelize.query(
        `SELECT outcome.* FROM outcome WHERE outcome.hid != -1 AND NOT EXISTS(SELECT * FROM handshake WHERE handshake.outcome_id = outcome.id AND handshake.side = 1 AND handshake.remaining_amount > 0) LIMIT 20`,
        { type: models.sequelize.QueryTypes.SELECT, raw: true }
      );
    },
    findOddByMatchID: function (matchId, idSupport, isDesc) {
        return models.Handshake
            .findOne({
                order: [
                    ['odds', isDesc ? 'DESC' : 'ASC']],
                where: {
                    match_id: matchId,
                    side: idSupport ? 1 : 2
                }
            });
    }
};
