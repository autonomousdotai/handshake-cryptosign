"""empty message

Revision ID: 29acd0fe9a40
Revises: c926a4509687
Create Date: 2019-02-17 23:51:07.396075

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '29acd0fe9a40'
down_revision = 'c926a4509687'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_token')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_token',
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('token_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['token_id'], [u'token.id'], name=u'user_token_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], [u'user.id'], name=u'user_token_ibfk_2'),
    sa.PrimaryKeyConstraint('user_id', 'token_id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    # ### end Alembic commands ###
