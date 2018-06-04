import * as crypto from 'crypto';
import * as jwt from 'jsonwebtoken';
import { InputError } from 'error.lib';

/**
 * generates random string of characters i.e salt
 * @function
 * @param {number} length - Length of the random string.
 */
export let genRandomString = (length: number): string => {
  return crypto
    .randomBytes(Math.ceil(length / 2))
    .toString('hex') /** convert to hexadecimal format */
    .slice(0, length);   /** return required number of characters */
};

export let hashPassword = (password: string): string => {
  return encrypt('sha512', password, '');
};

export let encrypt = (algorithm: string, value: string, salt: string): string => {
  return crypto.createHmac(algorithm, salt).update(value).digest('hex');
};

export let genToken = ((data: any, _ttl?: any): string => {
  const secret = process.env.JWT_SECRET,
        issuer = process.env.JWT_ISSUER,
        ttl = _ttl || process.env.JWT_TTL;
  return jwt.sign(data, secret, { expiresIn: ttl, issuer: issuer});
});

export let verifyToken = (token: string): object => {
  const secret = process.env.JWT_SECRET,
        issuer = process.env.JWT_ISSUER,
        ttl = process.env.JWT_TTL;
  try {
    return jwt.verify(token, secret, { maxAge: ttl, issuer: issuer}) as object;
  } catch (error) {
      const err = error.toString();
      if (err.indexOf('jwt expired')) {
        throw new InputError({token: 'auth.token.expired'});
      }
      throw new InputError({token: 'auth.token.incorrect'});
  }
};
