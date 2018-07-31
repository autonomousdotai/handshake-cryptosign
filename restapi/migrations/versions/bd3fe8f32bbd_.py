"""empty message

Revision ID: bd3fe8f32bbd
Revises: a0955ba03c81
Create Date: 2018-07-17 12:21:40.451290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd3fe8f32bbd'
down_revision = 'a0955ba03c81'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('category', sa.Column('approved', sa.Integer(), server_default='-1', nullable=True))
    op.add_column('outcome', sa.Column('total_amount', sa.Numeric(precision=20, scale=18), nullable=True))
    op.add_column('outcome', sa.Column('total_amount_dispute', sa.Numeric(precision=20, scale=18), nullable=True))
    # op.add_column('source', sa.Column('url', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_column('source', 'url')
    op.drop_column('outcome', 'total_amount_dispute')
    op.drop_column('outcome', 'total_amount')
    # op.drop_column('category', 'approved')
    # ### end Alembic commands ###
