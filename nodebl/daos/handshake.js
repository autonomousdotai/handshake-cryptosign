const models = require('../models');

module.exports = {
    create: (data) => {
        return new Promise((resolve, reject ) => {
        // models.sequelize.transaction({ autocommit: false }, (tx) => {
          models.sequelize.transaction({}, (tx) => {
            return models.Handshake
            .create(data, {
              transaction: tx
            })
            .then(async (result) => {
                // await tx.commit();
                return resolve(result);
            })
            .catch(async (err) => {
                await transaction.rollback();
                return reject(err);
            })
          });
        });
    },
    getById: (id) => {
        return models.Handshake
        .findOne({
            where: {
                id: id,
                deleted: 0
            }
        });
    }
};
