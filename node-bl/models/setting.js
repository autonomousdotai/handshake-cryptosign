
'use strict';
module.exports = (sequelize, DataTypes) => {
  var Setting = sequelize.define('Setting', {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
      allowNull: false,
      unique: true,
    },
    name: DataTypes.STRING,
    status: DataTypes.INTEGER
  }, {
    tableName: 'setting',
    timestamps: false,
    underscored: true,
  });

  return Setting;
};
