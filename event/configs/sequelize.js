var config = require('./');

module.exports = {
  development: {
    username: config.db.username,
    password: config.db.password,
    database: config.db.database,
    host: config.db.host,
    dialect: config.db.dialect,
  },
  staging: {
    username: config.db.username,
    password: config.db.password,
    database: config.db.database,
    host: config.db.host,
    dialect: config.db.dialect,
  },
  production: {
    username: config.db.username,
    password: config.db.password,
    database: config.db.database,
    host: config.db.host,
    dialect: config.db.dialect,
  }
};
