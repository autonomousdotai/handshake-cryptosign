
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
    data: DataTypes.TEXT,
    status: DataTypes.INTEGER
  }, {
    tableName: 'task',
    timestamps: false,
    underscored: true,
  });

  return Task;
};
