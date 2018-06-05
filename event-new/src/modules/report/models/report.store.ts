import { getDbConnection as db } from 'mysql.cfg';
import { Observable } from 'rxjs';
import { Transaction } from 'sequelize';
import { InputError } from 'error.lib';

const saveToDb = (tx: Transaction, data: any): Observable<any> => {
    return db().tables['Report'].create(data, {transaction: tx});
};

export const save = (data: any): Observable<any> => {
    return Observable
    .fromPromise(db().sequelize.transaction())
    .flatMap(tx => saveToDb(tx, data))
    .catch((err) => {
        return Observable.throw(new InputError({error: err}));
    });
};

export const createReportTnx = (data: any): Observable<any> => {
    return undefined;
};
