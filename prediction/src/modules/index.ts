import { Express } from 'express';

export let initModules = (app: Express) => {
    // default options
  app.use('/api/report', require('./report/index'));
};
