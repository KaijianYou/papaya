"""empty message

Revision ID: 9c3ba1541b26
Revises: a54b85ff33ca
Create Date: 2017-09-21 19:03:39.250429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c3ba1541b26'
down_revision = 'a54b85ff33ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_collections_owner_id', table_name='collections')
    op.create_foreign_key(None, 'collections', 'users', ['owner_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'collections', type_='foreignkey')
    op.create_index('ix_collections_owner_id', 'collections', ['owner_id'], unique=False)
    # ### end Alembic commands ###
