"""modify table posts

Revision ID: ba942a0829e4
Revises: fda17a93de46
Create Date: 2017-03-29 15:02:37.837624

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ba942a0829e4'
down_revision = 'fda17a93de46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_posts_timestamp', table_name='posts')
    op.drop_column('posts', 'timestamp')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.create_index('ix_posts_timestamp', 'posts', ['timestamp'], unique=False)
    # ### end Alembic commands ###