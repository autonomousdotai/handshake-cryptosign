import { getDbConnection as knex } from 'mysql.cfg';
import * as Knex from 'knex';

export const Table = {
  name: 'report',
  table: () => {
    knex().schema.hasTable('report').then((exists: boolean) => {
      if (!exists) {
        console.log('Table report does not exist, create new Table!');
        return knex().schema.createTable('report', (t: Knex.CreateTableBuilder) => {
          t.increments('id').primary();
          t.string('hid', 100);
          t.string('tnx_hash');
          t.string('status', 20);
          t.timestamps(true, true);
        });
      }
    }).catch((err: any) => {
      console.log(err.toString());
    });
  }
};
