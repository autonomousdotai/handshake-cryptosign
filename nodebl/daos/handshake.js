const models = require('../models');
const configs = require('../configs');
const network_id = configs.network_id;
const ownerAddress = configs.network[network_id].ownerAddress;
const Op = models.Sequelize.Op;
const moment = require('moment');

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
    },
    getAllMasterCollect: (fromId) => {
        return models.Handshake.findAll({
            where: {
                id: {
                    $gt: fromId || 0
                },
                [Op.or]: [{
                    status: 0 // STATUS_INITED
                }, {
                    status: 5 // STATUS_RESOLVED
                }],
                amount: {
                    $eq: models.sequelize.col('remaining_amount')
                },
                from_address: ownerAddress,
                contract_address: {
                    $ne: null
                },
				contract_json: {
                    $ne: null
                }
            },
            limit: 10
        });
    },
    multiUpdateStatusById: (ids, status) => {
        return models.Handshake.update({
            status: status,
            date_modified: moment().utc().format("YYYY-MM-DD HH:mm:ss")
        }, {
            where: {
                id: ids
            }
        });
    },
};
