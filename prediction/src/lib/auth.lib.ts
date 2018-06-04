import { Request } from 'express';
import { verifyToken } from 'utils.lib';
import { Observable } from 'rxjs';
import { InputError } from 'error.lib';

export let auth = (req: Request): Observable<any> => {
  return Observable
    .of(req.header('authorization') || '')
    .map(auth => auth.split(' '))
    .filter(tokens => tokens[0] === 'Bearer' && tokens[1] !== undefined)
    .defaultIfEmpty()
    .map(tokens => {
      if (!tokens) {
        throw new InputError({ token: 'auth.token.notFound' });
      }
      return verifyToken(tokens[1]);
    })
    .map((tokenInfo: any) => {
      return tokenInfo;
    }
  );
};
