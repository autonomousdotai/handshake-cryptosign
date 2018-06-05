import { Observable } from 'rxjs';
import { validate } from 'class-validator';
import { ValidateError } from 'error.lib';


export let isValid = <T>(clazzInstance: T): Observable<T> => {
  return Observable
    .fromPromise(validate(clazzInstance))
    .map(errors => {
      if (errors.length > 0) {
        throw new ValidateError(errors);
      }
      return clazzInstance;
    });
};
