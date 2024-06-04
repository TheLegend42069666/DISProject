"""empty message

Revision ID: 7c00b1d45bbe
Revises: 
Create Date: 2024-06-04 17:55:45.992571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c00b1d45bbe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price', sa.Integer(), nullable=False))
        batch_op.drop_column('int')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.add_column(sa.Column('int', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_column('price')

    # ### end Alembic commands ###
