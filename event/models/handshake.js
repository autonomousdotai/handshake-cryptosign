'use strict';
module.exports = (sequelize, DataTypes) => {
  var Handshake = sequelize.define('Handshake', {
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
    hs_type: DataTypes.INTEGER,
    extra_data: DataTypes.TEXT,
    chain_id: DataTypes.INTEGER,
    state: DataTypes.INTEGER,
    is_private: DataTypes.INTEGER,
    description: DataTypes.TEXT,
    status: DataTypes.INTEGER,
    bk_status: DataTypes.INTEGER,
    shake_count: DataTypes.INTEGER,
    view_count: DataTypes.INTEGER,
    comment_count: DataTypes.INTEGER,
    from_address: DataTypes.STRING,
    odds: DataTypes.INTEGER,
    amount: DataTypes.INTEGER,
    remaining_amount: DataTypes.INTEGER,
    win_value: DataTypes.INTEGER,
    currency: DataTypes.STRING,
    side: DataTypes.INTEGER,
    user_id: DataTypes.INTEGER,
    outcome_id: DataTypes.INTEGER,
    modified_user_id: DataTypes.INTEGER,
    created_user_id: DataTypes.INTEGER,
  }, {
    tableName: 'handshake',
    timestamps: false,
    underscored: true,
  });

  return Handshake;
};
