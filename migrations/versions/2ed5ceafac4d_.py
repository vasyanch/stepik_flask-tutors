"""empty message

Revision ID: 2ed5ceafac4d
Revises: 
Create Date: 2020-04-21 04:37:08.293241

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '2ed5ceafac4d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('day_times_',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.Time(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('time')
    )
    op.create_table('goals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.Column('emoji', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('value')
    )
    op.create_table('teachers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('about', sa.Text(), nullable=False),
    sa.Column('picture', sa.String(), nullable=False),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('weekdays',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('day_name', sa.String(length=11), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('day_name')
    )
    op.create_table('association_teacher_goals',
    sa.Column('Teacher', sa.Integer(), nullable=False),
    sa.Column('Goal', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['Goal'], ['goals.id'], ),
    sa.ForeignKeyConstraint(['Teacher'], ['teachers.id'], )
    )
    op.create_table('lessons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.Column('day_name_id', sa.Integer(), nullable=False),
    sa.Column('time_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['day_name_id'], ['weekdays.id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ),
    sa.ForeignKeyConstraint(['time_id'], ['day_times_.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('goal_id', sa.Integer(), nullable=False),
    sa.Column('free_time', sa.String(), nullable=False),
    sa.Column('client_name', sa.String(), nullable=False),
    sa.Column('client_phone', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bookings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_name', sa.String(), nullable=False),
    sa.Column('client_phone', sa.String(), nullable=False),
    sa.Column('lesson_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bookings')
    op.drop_table('requests')
    op.drop_table('lessons')
    op.drop_table('association_teacher_goals')
    op.drop_table('weekdays')
    op.drop_table('teachers')
    op.drop_table('goals')
    op.drop_table('day_times_')
    # ### end Alembic commands ###
