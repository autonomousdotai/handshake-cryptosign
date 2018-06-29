'use strict';
module.exports = (sequelize, DataTypes) => {
  var Outcome = sequelize.define('Outcome', {
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
    name: DataTypes.STRING,
    match_id: DataTypes.INTEGER,
    hid: DataTypes.STRING,
    result: DataTypes.INTEGER,
    tx: DataTypes.STRING,
    modified_user_id: DataTypes.INTEGER,
    created_user_id: DataTypes.INTEGER,
  }, {
    tableName: 'outcome',
    timestamps: false,
    underscored: true,
  });

  return Outcome;
};
