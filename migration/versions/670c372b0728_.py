"""empty message

Revision ID: 670c372b0728
Revises: 
Create Date: 2020-06-05 10:58:19.929869

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '670c372b0728'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('example_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('join_date', sa.DateTime(), nullable=False),
    sa.Column('vip', sa.Boolean(), nullable=False),
    sa.Column('number', sa.Float(), nullable=False),
    sa.Column('data', sa.PickleType(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='example'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('example_table', schema='example')
    # ### end Alembic commands ###
