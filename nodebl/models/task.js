
'use strict';
module.exports = (sequelize, DataTypes) => {
  var Task = sequelize.define('Task', {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
      allowNull: false,
      unique: true,
    },
    task_type: DataTypes.STRING,
    action: DataTypes.STRING,
    data: DataTypes.TEXT,
    status: DataTypes.INTEGER,
    contract_address: DataTypes.STRING,
    contract_json: DataTypes.STRING
  }, {
    tableName: 'task',
    timestamps: false,
    underscored: true,
  });

  return Task;
};
