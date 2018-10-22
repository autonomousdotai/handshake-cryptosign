"""empty message

Revision ID: 57cf0a7f396f
Revises: 564abd7bdc60
Create Date: 2018-10-22 06:34:57.436543

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '57cf0a7f396f'
down_revision = '564abd7bdc60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('redeem', 'code',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
    op.create_unique_constraint(None, 'redeem', ['code'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'redeem', type_='unique')
    op.alter_column('redeem', 'code',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
    # ### end Alembic commands ###
