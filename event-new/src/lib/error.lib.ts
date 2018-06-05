import { ValidationError } from 'class-validator';
import * as _ from 'lodash';

export class InputError extends Error {
  constructor(message: any) {
    if (message && typeof(message.message) === 'string') {
      message.message = {
        error: message.message
      };
    }
    super(JSON.stringify(message));
  }
}

export class ValidateError extends Error {
  constructor(err: ValidationError[]) {
    const result: any = {};
    _.forEach(err, (item: ValidationError) => {
      result[item.property] = _.values(item.constraints);
    });
    super(JSON.stringify(result));
  }
}

export class DbError extends Error {
  constructor(error: any) {
    super(error);
  }
}