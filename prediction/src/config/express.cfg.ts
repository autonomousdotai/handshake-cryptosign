/**
 * Module dependencies.
 */
import { Express, Request, Response, NextFunction } from 'express';
import * as compression from 'compression';  // compresses requests
import * as bodyParser from 'body-parser';
import * as helmet from 'helmet';
import { InputError, ValidateError, DbError } from 'error.lib';

/**
 * Initialize vars
 */
const sessionTTL = +process.env.SESSION_TTL * 24 * 60 * 60, // = 14 days. Default
  payloadSize = process.env.PAYLOAD_SIZE;

/**
 * Initialize application middleware
 */
export let initMiddleware = (app: Express) => {
  // Should be placed before static
  app.use(compression({
    filter: (req: Request, res: Response) => {
      if (req.headers['x-no-compression']) {
        // don't compress responses with this request header
        return false;
      }
      return (/json|text|javascript|css|font|svg/).test(res.getHeader('Content-Type').toString());
    },
    level: 9
  }));

  // Request body parsing middleware should be above methodOverride
  app.use(bodyParser.json({ limit: payloadSize }));
  app.use(bodyParser.urlencoded({ limit: payloadSize, extended: true }));
};

/**
 * Configure Helmet headers configuration
 */
export let initHelmetHeaders = (app: Express) => {
  // Use helmet to secure Express headers
  app.use(helmet.noCache());
  app.use(helmet.frameguard());
  app.disable('x-powered-by');
  app.use(helmet.contentSecurityPolicy({
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", 'maxcdn.bootstrapcdn.com']
    }
  }));
  app.use(helmet.hsts({
    maxAge: sessionTTL,
    includeSubdomains: true,
    force: true
  }));
  app.use(helmet.ieNoOpen());
  app.use(helmet.noSniff());
  app.use(helmet.referrerPolicy({ policy: 'same-origin' }));
  // Sets "X-XSS-Protection: 1; mode=block".
  app.use(helmet.xssFilter());
};

/**
 * Configure error handling
 */
export let initErrorRoutes = (app: Express) => {
  app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
    try {
      decodeURIComponent(req.path);
    }
    catch (e) {
      return res.status(404).json({url: 'not_found'});
    }

    // If the error object doesn't exists
    if (!err) {
      return next();
    }

    // expected errors
    if (err instanceof InputError || err instanceof ValidateError) {
      return res.status(400).json(JSON.parse(err.message));
    }
    else if (err instanceof DbError) {
      return res.status(400).json({ message: err.message });
    }
    const _err = err as any;
    if (_err.status === 400 && _err.type === 'entity.parse.failed' && _err.body) {
      return res.status(400).json({
        message: 'request.body.JSON.invalid'
      });
    }

    // Log unexpected errors
    console.error(err.stack);
    // Redirect to error page
    res.status(500).json({
      message: 'error.500'
    });
  });
};

export let initExpress = (app: Express) => {
  // Initialize Express middleware
  initMiddleware(app);

  // Initialize Helmet security headers
  initHelmetHeaders(app);
};
