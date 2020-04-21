"""empty message

Revision ID: 2ed5ceafac4d
Revises: 
Create Date: 2020-04-21 04:37:08.293241

"""
import json
from time import sleep
from datetime import time as tim

import sqlalchemy as sa
from alembic import op

from app import db
from models import Teacher, Goal, Lesson, Time, WeekDay

# revision identifiers, used by Alembic.
revision = '2ed5ceafac4d'
down_revision = None
branch_labels = None
depends_on = None


def insert_test_data():
    sleep(10)
    with open('test_data.json', 'r', encoding='utf8') as _file:
        data = json.load(_file)
    all_objects = []

    week_days = [
        WeekDay(id=_id, day_name=day_name) for _id, day_name in [
            (1, 'Понедельник'), (2, 'Вторник'), (3, 'Среда'), (4, 'Четверг'),
            (5, 'Пятница'), (6, 'Суббота'), (7, 'Воскресенье')
        ]
    ]
    all_objects.extend(week_days)

    times = [
        Time(id=id_time[0], time=id_time[1]) for id_time in [
            (1, tim(8)), (2, tim(10)), (3, tim(12)), (4, tim(14)), (5, tim(16)),
            (6, tim(18)), (7, tim(20)), (8, tim(22))
        ]
    ]
    all_objects.extend(times)

    goals = \
        [Goal(id=int(goal_id), value=goal_data[0], emoji=goal_data[1]) for goal_id, goal_data in data['goals'].items()]
    all_objects.extend(goals)

    teachers = []
    lessons = []
    lesson_id = 1
    for teacher_dict in data['teachers']:
        teacher_ = Teacher(
            id=int(teacher_dict['id']) + 1,
            name=teacher_dict['name'],
            about=teacher_dict['about'],
            rating=teacher_dict['rating'],
            picture=teacher_dict['picture'],
            price=teacher_dict['price'],
            goals=list(filter(lambda x: x.id in [int(i) for i in teacher_dict['goals']], goals))
        )
        teachers.append(teacher_)
        for day_id, time_status in teacher_dict['free'].items():
            for _time, status in time_status.items():
                _time = tim(int(_time.split(':')[0]))
                _time_id = list(filter(lambda x: x.time == _time, times))[0].id
                lesson = Lesson(
                    id=lesson_id, teacher_id=teacher_.id, day_name_id=int(day_id), time_id=_time_id, status=status
                )
                lessons.append(lesson)
                lesson_id += 1

    all_objects.extend(teachers)
    all_objects.extend(lessons)

    db.session.add_all(all_objects)
    db.session.commit()


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
    db.session.commit()
    insert_test_data()
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
