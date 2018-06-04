/**
 * Load environment variables from .env file, where API keys and passwords are configured.
 */
require('dotenv').config({ path: '.env' });
const del = /^win/.test(process.platform) ? ';' : ':';

process.env.NODE_PATH = __dirname + `/config${del}` + __dirname + '/lib';
require('module').Module._initPaths();

/**
 * Module dependencies.
 */
import * as express from 'express';
import { connectDB, createTable } from 'mysql.cfg';
import { initExpress, initErrorRoutes } from 'express.cfg';
import { connectWeb3Server } from 'web3.cfg';
import { initModules } from './modules';

/**
 * Initialize vars
 */
const appPort = process.env.PORT || process.env.NODE_PORT,
  appEnv = process.env.NODE_ENV,
  mysqlConfig = {
    host: process.env.MYSQL_HOST,
    user: process.env.MYSQL_USER,
    password: process.env.MYSQL_PWD,
    database: process.env.MYSQL_DBNAME
  },
  web3Config = {
    http: process.env.HTTP_PROVIDER,
    ws: process.env.WS_PROVIDER,
    ipc: process.env.IPC_PROVIDER
  };

// Create Express server.
const app = express();

const start = async () => {
  // Connect to Mysql.
  connectDB(mysqlConfig);
  createTable();

  // Express configuration.
  initExpress(app);

  // wire Express vertical modules
  initModules(app);

  // init error routers
  initErrorRoutes(app);

  // init web3 provider
  connectWeb3Server(web3Config);

  // Start Express server.
  exports.app = app.listen(appPort, () => {
    console.log('App is running at http://localhost:%d in %s mode', appPort, appEnv);
    console.log('Press CTRL-C to stop\n');
  });
};

start().catch(console.error);

export let server = app;

