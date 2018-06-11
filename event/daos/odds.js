const models = require('../models');

// side: 0 (unknown), 1 (support), 2 (against)
module.exports = {
  // LIMIT 20 records
  getAgainstOddsNull: function () {
    return models.sequelize.query(
      `SELECT outcome.* FROM outcome WHERE outcome.hid != -1 AND NOT EXISTS(SELECT * FROM handshake WHERE handshake.outcome_id = outcome.id AND handshake.side = 2 AND handshake.remaining_amount > 0) LIMIT 20`,
      { type: models.sequelize.QueryTypes.SELECT, raw: true }
    );
  },
  // LIMIT 20 records
  getSupportOddsNull: function () {
    return models.sequelize.query(
      `SELECT outcome.* FROM outcome WHERE outcome.hid != -1 AND NOT EXISTS(SELECT * FROM handshake WHERE handshake.outcome_id = outcome.id AND handshake.side = 1 AND handshake.remaining_amount > 0) LIMIT 20`,
      { type: models.sequelize.QueryTypes.SELECT, raw: true }
    );
  }
};
