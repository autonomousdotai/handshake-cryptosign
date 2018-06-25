'use strict';
module.exports = (sequelize, DataTypes) => {
  var Event = sequelize.define('Event', {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
      allowNull: false,
      unique: true,
    },
    address: DataTypes.STRING,
    event_name: DataTypes.STRING,
    value: DataTypes.STRING,
    block: DataTypes.INTEGER,
    date_created: DataTypes.DATE,
    log_index: DataTypes.INTEGER,
  }, {
    tableName: 'event',
    timestamps: false,
    underscored: true,
  });

  return Event;
};
