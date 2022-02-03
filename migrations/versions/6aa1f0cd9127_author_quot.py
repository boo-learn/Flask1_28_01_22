"""Author+Quot

Revision ID: 6aa1f0cd9127
Revises: 
Create Date: 2022-02-03 19:35:50.469135

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6aa1f0cd9127'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quote_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author', sa.String(length=32), nullable=True),
    sa.Column('text', sa.String(length=255), nullable=True),
    sa.Column('rate', sa.Integer(), server_default='1', nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('quote_model')
    # ### end Alembic commands ###
