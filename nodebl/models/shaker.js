'use strict';
module.exports = (sequelize, DataTypes) => {
  var Shaker = sequelize.define('Shaker', {
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
    shaker_id: DataTypes.INTEGER,
    amount: DataTypes.DECIMAL(36, 18),
    remaining_amount: DataTypes.DECIMAL(36, 18),
    handshake_id: DataTypes.INTEGER,
    free_bet: DataTypes.INTEGER,
    status: DataTypes.INTEGER,
    bk_status: DataTypes.INTEGER,
    currency: DataTypes.STRING,
    side: DataTypes.INTEGER,
    modified_user_id: DataTypes.INTEGER,
    created_user_id: DataTypes.INTEGER,
    chain_id: DataTypes.INTEGER,
    from_address: DataTypes.STRING,
    contract_address: DataTypes.STRING,
    contract_json: DataTypes.STRING,
    from_request: DataTypes.STRING,
    history_id: DataTypes.INTEGER
  }, {
    tableName: 'shaker',
    timestamps: false,
    underscored: true,
  });

  return Shaker;
};
