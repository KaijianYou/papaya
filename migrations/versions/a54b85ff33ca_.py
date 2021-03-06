"""empty message

Revision ID: a54b85ff33ca
Revises: 03796eba455d
Create Date: 2017-09-21 18:09:44.447986

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a54b85ff33ca'
down_revision = '03796eba455d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('collections',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('create_datetime', sa.DateTime(), nullable=True),
    sa.Column('update_datetime', sa.DateTime(), nullable=True),
    sa.Column('enable', sa.Boolean(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_collections_item_id'), 'collections', ['item_id'], unique=False)
    op.create_index(op.f('ix_collections_owner_id'), 'collections', ['owner_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_collections_owner_id'), table_name='collections')
    op.drop_index(op.f('ix_collections_item_id'), table_name='collections')
    op.drop_table('collections')
    # ### end Alembic commands ###
