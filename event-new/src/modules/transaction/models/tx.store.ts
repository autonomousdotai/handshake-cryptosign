
import { getDbConnection as db } from 'mysql.cfg';
const constants = require('../../../constants/constants');


export const getAllPending = () => {
  return db().tables.Tx.findAll({
    order: [
      ['date_created', 'DESC']],
    where: {
      status: constants.Tx.STATUS_PENDING,
    }
  });
};
