
import { getDbConnection as knex } from 'mysql.cfg';
import { Observable } from 'rxjs';
import { InputError } from 'error.lib';

export const save = (data: any): Observable<any> => {
    const DB = knex()('report');
    const dataSave = DB.insert(data).then( (result) => {
        return result;
    });
    return Observable
    .fromPromise(dataSave)
    .catch((err) => {
        return Observable.throw(new InputError({error: err}));
    });
};

export const createReportTnx = (data: any): Observable<any> => {
    return undefined;
};