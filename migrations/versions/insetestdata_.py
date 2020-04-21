import json
from datetime import time as tim

from app import db
from models import Teacher, Goal, Lesson, Time, WeekDay


def insert_test_data():
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


revision = 'insetestdata'
down_revision = '2ed5ceafac4d'
branch_labels = None
depends_on = None


def upgrade():
    insert_test_data()
