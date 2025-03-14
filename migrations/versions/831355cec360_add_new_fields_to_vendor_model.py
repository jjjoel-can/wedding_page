"""Add new fields to Vendor model

Revision ID: 831355cec360
Revises: 32e1ce969b94
Create Date: 2025-03-14 20:49:10.727679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '831355cec360'
down_revision = '32e1ce969b94'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vendors', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('instagram', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('facebook', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('twitter', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('linkedin', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('youtube', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('tiktok', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('pinterest', sa.String(length=200), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vendors', schema=None) as batch_op:
        batch_op.drop_column('pinterest')
        batch_op.drop_column('tiktok')
        batch_op.drop_column('youtube')
        batch_op.drop_column('linkedin')
        batch_op.drop_column('twitter')
        batch_op.drop_column('facebook')
        batch_op.drop_column('instagram')
        batch_op.drop_column('website')

    # ### end Alembic commands ###
