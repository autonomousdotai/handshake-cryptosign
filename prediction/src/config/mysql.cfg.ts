
import * as glob from 'glob';
import * as Knex from 'knex';

let connection: Knex;
/**
 * create mysql connection
 */
export let connectDB = ( options: any ) => {
  try {
    connection = Knex({
      client: 'mysql',
      connection: {
        host: options.host,
        user: options.user,
        password: options.password,
        database: options.database
      },
      pool: {
        min: 2,
        max: 10
      },
      // debug: true
    });
    console.log('Connected to mysql db');
  } catch (error) {
    console.error('Failed to connect to mysql', error);
  }
};

/**
 * get mysql connection
 */
export let getDbConnection = (): Knex => {
  if (!connection) {
    throw 'Database is not yet instantiated';
  }
  return connection;
};


export let createTable = () => {
  let tableInstances: any[] = [];
  glob('**/*.model.ts', {}, (err, files) => {
    files.forEach(file => {
      tableInstances = tableInstances.concat(require(file.replace('.ts', '').replace('src', '..')).Table || []);
    });
    console.log('Begin check tables existed.');
    const tasks = [] as any;
    tableInstances.forEach((item: any) => {
      item.table();
    });
    Promise.all(tasks).then(result => {
      console.log('Check tables existed done!');
    }).catch(err => {
      console.error(err);
    });
  });
};
