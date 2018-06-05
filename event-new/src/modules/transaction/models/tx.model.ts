
import { Sequelize, INTEGER, STRING, TEXT, Instance } from 'sequelize';

type TxInstance = Instance<TxAttributes> & TxAttributes;

interface TxAttributes {
    id?: number;
    hash: string;
    scope: string;
    contract_name: string;
    contract_address: string;
    contract_method: string;
    arguments: string;
    payload: string;
    from_address: string;
    to_address: string;
    amount: string;
    user_id: number;
    status: number;
    transaction_status: string;
    chain_id: number;
}

export const Table = {
  name: 'Tx',
  table: (sequalize: Sequelize) => {
    return sequalize.define<TxInstance, TxAttributes>('Tx', {
        id: {
            type: INTEGER,
            autoIncrement: true,
            primaryKey: true,
            allowNull: false,
            unique: true,
        },
            hash: STRING,
            scope: STRING,
            contract_name: STRING,
            contract_address: STRING,
            contract_method: STRING,
            arguments: STRING,
            payload: TEXT,
            from_address: STRING,
            to_address: STRING,
            amount: STRING,
            user_id: INTEGER,
            status: INTEGER,
            transaction_status: STRING,
            chain_id: INTEGER
        }, {
            tableName: 'tx',
            timestamps: false,
            underscored: true,
        });
    }
};
