"""empty message

Revision ID: 3fda017ffa89
Revises: 29acd0fe9a40
Create Date: 2019-02-17 23:52:54.563511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3fda017ffa89'
down_revision = '29acd0fe9a40'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('token_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Integer(), server_default='-1', nullable=True),
    sa.Column('hash', sa.String(length=255), nullable=True),
    sa.Column('modified_user_id', sa.Integer(), nullable=True),
    sa.Column('created_user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['modified_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['token_id'], ['token.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id', 'user_id', 'token_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_token')
    # ### end Alembic commands ###
