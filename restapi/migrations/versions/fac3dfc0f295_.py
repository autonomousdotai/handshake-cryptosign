"""empty message

Revision ID: fac3dfc0f295
Revises: ec7f9015e5af
Create Date: 2018-11-21 17:31:07.624746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fac3dfc0f295'
down_revision = 'ec7f9015e5af'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_user_disable_popup', sa.Integer(), server_default='0', nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_user_disable_popup')
    # ### end Alembic commands ###