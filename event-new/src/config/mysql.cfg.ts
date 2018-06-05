
import * as glob from 'glob';
import * as Sequelize from 'sequelize';

export interface IDb {
  sequelize: Sequelize.Sequelize;
  Sequelize: Sequelize.SequelizeStatic;
  tables: any;
}

let db: IDb;
/**
 * create mysql connection
 */
export let connectDB = async ( options: any ) => {
  try {
    //  new Sequelize(process.env[config.use_env_variable], config);
    const sequelize = new Sequelize(options.database, options.username, options.password, options);
    console.log('Connected to mysql db');

    let tableInstances: any[] = [];
    glob('**/*.model.ts', {}, (err, files) => {
      files.forEach(file => {
        tableInstances = tableInstances.concat(require(file.replace('.ts', '').replace('src', '..')).Table || []);
      });
      console.log('Begin check tables existed.');
      const tasks = [] as any;
      const _db: IDb = {
        sequelize,
        Sequelize,
        tables: {}
      };
      tableInstances.forEach((item: any) => {
        Object.assign(_db.tables, {[item.name]: item.table(sequelize)});
        if (_db.tables[item.name].associate) {
          _db.tables[item.name].associate(_db);
        }
      });
      Promise.all(tasks).then(result => {
        db = _db;
        console.log('Check tables done!');
      }).catch(err => {
        console.error(err);
      });
    });

  } catch (error) {
    console.error('Failed to connect to mysql', error);
  }
};

/**
 * get mysql connection
 */
export let getDbConnection = (): IDb => {
  if (!db) {
    throw 'Database is not yet instantiated';
  }
  return db;
};
