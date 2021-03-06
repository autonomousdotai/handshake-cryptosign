"""empty message

Revision ID: 62696912de3e
Revises: 5b1c6d82dde8
Create Date: 2018-10-16 14:34:53.852993

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '62696912de3e'
down_revision = '5b1c6d82dde8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('onchain_task', 'description')
    op.drop_column('onchain_task', 'is_erc20')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('onchain_task', sa.Column('is_erc20', mysql.INTEGER(display_width=11), server_default=sa.text(u"'0'"), autoincrement=False, nullable=True))
    op.add_column('onchain_task', sa.Column('description', mysql.VARCHAR(length=255), nullable=True))
    # ### end Alembic commands ###
