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
    index: DataTypes.INTEGER,
    contract_id: DataTypes.INTEGER,
    total_amount: DataTypes.DECIMAL(36, 18),
    total_dispute_amount: DataTypes.DECIMAL(36, 18),
    modified_user_id: DataTypes.INTEGER,
    created_user_id: DataTypes.INTEGER
  }, {
    tableName: 'outcome',
    timestamps: false,
    underscored: true,
  });

  return Outcome;
};
