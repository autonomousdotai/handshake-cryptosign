"""empty message

Revision ID: 69f427fe4c14
Revises: 79df2fb3e8a9
Create Date: 2018-09-25 16:12:19.725703

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '69f427fe4c14'
down_revision = '79df2fb3e8a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('match', sa.Column('public', sa.Integer(), server_default='1', nullable=True))
    op.drop_column('outcome', 'public')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('outcome', sa.Column('public', mysql.INTEGER(display_width=11), server_default=sa.text(u"'1'"), autoincrement=False, nullable=True))
    op.drop_column('match', 'public')
    # ### end Alembic commands ###
