
import { Sequelize, INTEGER, STRING, DATE, Instance } from 'sequelize';

type EventInstance = Instance<EventAttributes> & EventAttributes;

interface EventAttributes {
    id?: number;
    address: string;
    event_name: string;
    value: string;
    block: number;
    date_created: Date;
    log_index: number;
}

export const Table = {
  name: 'Event',
  table: (sequalize: Sequelize) => {
    return sequalize.define<EventInstance, EventAttributes>('Event', {
        id: {
            type: INTEGER,
            autoIncrement: true,
            primaryKey: true,
            allowNull: false,
            unique: true,
        },
            address: STRING,
            event_name: STRING,
            value: STRING,
            block: INTEGER,
            date_created: DATE,
            log_index: INTEGER,
        }, {
            tableName: 'event',
            timestamps: false,
            underscored: true,
        });
  }
};
