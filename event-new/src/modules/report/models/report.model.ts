import { Sequelize, INTEGER, STRING, UUID, Instance } from 'sequelize';

type ReportInstance = Instance<ReportAttributes> & ReportAttributes;

interface ReportAttributes {
  id?: number;
  name: string;
  price: string;
  archived?: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export const Table = {
  name: 'Report',
  table: (sequalize: Sequelize) => {
    return sequalize.define<ReportInstance, ReportAttributes>('Report', {
      id: {
        type: UUID,
        autoIncrement: true,
        primaryKey: true,
        allowNull: false,
        unique: true,
      },
      hid: INTEGER,
      tnx_hash: STRING,
      status: STRING,
      outcome: INTEGER
    }, {
      tableName: 'report',
      timestamps: false,
      underscored: true,
    });
  }
};
