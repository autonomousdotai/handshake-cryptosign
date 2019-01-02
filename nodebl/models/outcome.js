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
    master_collect_status: DataTypes.STRING,
    modified_user_id: DataTypes.INTEGER,
    created_user_id: DataTypes.INTEGER
  }, {
    tableName: 'outcome',
    timestamps: false,
    underscored: true,
  });

  Outcome.associate = function (models) {
    Outcome.hasMany(models.Handshake, {
      foreignKey: 'outcome_id',
      sourceKey: 'id'
    });
    Outcome.belongsTo(models.Match, { 
      foreignKey: 'match_id',
      sourceKey: 'id'
    })
  };
  return Outcome;
};
