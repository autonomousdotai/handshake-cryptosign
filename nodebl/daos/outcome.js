const models = require('../models');
const moment = require('moment');
const Op = models.Sequelize.Op;

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
                hid: hid,
                date_modified: moment().utc().format("YYYY-MM-DD HH:mm:ss")
            });
    },
    getAllMasterCollect: () => {
        return models.Outcome.findAll({
            where: {
                hid: {
                    $gte: 0
                },
                [Op.or]: [{
                    master_collect_status: null
                }, {
                    master_collect_status: ""
                }],
                deleted: 0
            },
            include: [
                {
                    model: models.Match,
                    as: 'Match',
                    where: {
                        deleted: 0,
                        disputeTime: {
                            [Op.lte]: Math.floor(+moment.utc()/1000)
                        }
                    }
                }
            ],
            limit: 10
        });
    },
    multiUpdateOutcomeMasterStatus: (ids, status) => {
        return models.Outcome.update({
            master_collect_status: status,
            date_modified: moment().utc().format("YYYY-MM-DD HH:mm:ss")
        }, {
            where: {
                id: ids
            }
        });
    }
};
