"""modify table users

Revision ID: e7791985bc77
Revises: 6d5c61aa2492
Create Date: 2017-02-27 14:56:00.653069

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7791985bc77'
down_revision = '6d5c61aa2492'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('about_me', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('last_visited', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('register_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'register_date')
    op.drop_column('users', 'location')
    op.drop_column('users', 'last_visited')
    op.drop_column('users', 'about_me')
    # ### end Alembic commands ###
