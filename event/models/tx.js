'use strict';
module.exports = (sequelize, DataTypes) => {
  var Tx = sequelize.define('Tx', {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
      allowNull: false,
      unique: true,
    },
    hash: DataTypes.STRING,
    scope: DataTypes.STRING,
    contract_name: DataTypes.STRING,
    contract_address: DataTypes.STRING,
    contract_method: DataTypes.STRING,
    arguments: DataTypes.STRING,
    payload: DataTypes.TEXT,
    from_address: DataTypes.STRING,
    to_address: DataTypes.STRING,
    amount: DataTypes.STRING,
    user_id: DataTypes.INTEGER,
    status: DataTypes.INTEGER,
    transaction_status: DataTypes.STRING,
    chain_id: DataTypes.INTEGER
  }, {
    tableName: 'tx',
    timestamps: false,
    underscored: true,
  });

  return Tx;
};
