'use strict';
module.exports = (sequelize, DataTypes) => {
  var Match = sequelize.define('Match', {
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
    homeTeamName: DataTypes.STRING,
    homeTeamCode: DataTypes.STRING,
    homeTeamFlag: DataTypes.STRING,
    awayTeamName: DataTypes.TEXT,
    awayTeamCode: DataTypes.STRING,
    awayTeamFlag: DataTypes.STRING,
    homeScore: DataTypes.INTEGER,
    awayScore: DataTypes.INTEGER,
    date: DataTypes.BIGINT,
    modified_user_id: DataTypes.INTEGER,
    created_user_id: DataTypes.INTEGER,
    name: DataTypes.STRING,
    market_fee: DataTypes.INTEGER
  }, {
    tableName: 'match',
    timestamps: false,
    underscored: true,
  });

  return Match;
};
