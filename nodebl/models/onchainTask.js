'use strict';
module.exports = (sequelize, DataTypes) => {
  var OnchainTask = sequelize.define('OnchainTask', {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
      allowNull: false,
      unique: true,
    },
    date_created: DataTypes.DATE,
    date_modified: DataTypes.DATE,
    deleted: DataTypes.INTEGER,
    contract_address: DataTypes.STRING,
    contract_json: DataTypes.STRING,
    contract_method: DataTypes.STRING,
    from_address: DataTypes.STRING,
    data: DataTypes.TEXT,
    status: DataTypes.INTEGER,
    task_id: DataTypes.INTEGER
  }, {
    tableName: 'onchain_task',
    timestamps: false,
    underscored: true,
  });

  return OnchainTask;
};
