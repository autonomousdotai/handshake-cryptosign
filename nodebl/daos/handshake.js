const models = require('../models');

module.exports = {
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
