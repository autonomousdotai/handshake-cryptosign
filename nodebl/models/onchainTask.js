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
    description: DataTypes.STRING,
    is_erc20: DataTypes.STRING, //ETH, ERC20
    address: DataTypes.STRING,
    contract_name: DataTypes.STRING,
    method_name: DataTypes.STRING,
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
