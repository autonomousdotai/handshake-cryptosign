import { getDbConnection as db } from 'mysql.cfg';

export const getByBlock = function (address: string, block: number, log_index: number) {
    return db().tables.Event
    .findOne({
        order: [
            ['id', 'DESC']],
        where: {
            address: address,
            block: block,
            log_index: log_index,
        }
    });
};

export const getLastLogByName = function (address: string, event_name: string) {
    return db().tables.Event
    .findOne({
        order: [
            ['id', 'DESC']],
        where: {
            address: address,
            event_name: event_name,
        }
    });
};

export const getAllLog = function () {
    return db().tables.Event
    .findAll({
        where: {
            event_name: 'CLICK_BUTTON'
        }
    });
};

export const create =  async function (address: string, event_name: string, value: any, block: number, log_index: number) {
    return db().tables.Event
        .create(
        {
            address: address,
            event_name: event_name,
            value: value,
            block: block,
            log_index: log_index,
            date_created: new Date(),
        }, {
            transaction: await db().sequelize.transaction()
        }
    );
};
