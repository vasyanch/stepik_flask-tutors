import json
import re

from random import randint
from flask import Flask, render_template, request, redirect


phone_template = re.compile(r"(^|\+)\d{11}$")

app = Flask(__name__)

database = {
    'main': 'db/goals_teachers.json',
    'booking': 'db/booking.json',
    'request': 'db/request.json'
}


@app.route('/')
def render_index():
    db_main_data = load_db_data(database['main'])
    teachers = db_main_data.get('teachers')
    teachers = [teachers[randint(0, len(teachers) - 1)] for i in range(6)]
    goals = db_main_data.get('goals')
    return render_template('index.html', teachers=teachers, goals=goals)


@app.route('/goals/<goal>/')
def render_goal(goal):
    db_main_data = load_db_data(database['main'])
    goal_teachers = list(filter(lambda x: goal in x['goals'], db_main_data.get('teachers')))
    sorted_goal_teachers = sort_by_key(for_sort=goal_teachers, sort_key='rating', reverse=True)
    goals = db_main_data.get('goals')
    return render_template('goal.html', goal=goals.get(goal), teachers=sorted_goal_teachers)


@app.route('/profiles/<teacher_id>/')
def render_profile(teacher_id):
    db_main_data = load_db_data(database['main'])
    teacher = get_teacher_by_id(teacher_list=db_main_data.get('teachers'), teacher_id=int(teacher_id))[0]
    week_days = get_week_days()
    goals = db_main_data.get('goals')
    return render_template('profile.html', teacher=teacher, week_days=week_days, goals=goals)


@app.route('/request/')
def render_request():
    return render_template('request.html')


@app.route('/request_done/', methods=['POST'])
def render_request_done():
    db_file_request = database['request']
    db_file_main = database['main']
    client_name = request.form.get('client_name')
    client_phone = request.form.get('client_phone')
    goal = request.form.get('goal')
    free_time = request.form.get('time')
    if not validate_username_phone(client_name, client_phone):
        return redirect('/request/')
    user_request = {
        'goal': goal,
        'free_time': free_time,
        'client_name': client_name,
        'client_phone': client_phone
    }
    db_requests = load_db_data(db_file_request)
    db_requests.append(user_request)
    dump_db_data(file_path=db_file_request, data=db_requests)
    goals = load_db_data(db_file_main).get('goals')
    free_time = free_time + ' часа в неделю' if free_time == '1-2' else free_time + ' часов в неделю'
    return render_template(
        'request_done.html', goal=goals.get(goal)[0], free_time=free_time, name=client_name, phone=client_phone
    )


@app.route('/booking/<teacher_id>/<week_day>/<day_time>/')
def render_booking(teacher_id, week_day, day_time):
    teacher = load_db_data(database['main']).get('teachers')[int(teacher_id)]
    week_days = get_week_days()
    return render_template('booking.html', teacher=teacher, week_day=week_day, day_time=day_time, week_days=week_days)


@app.route('/booking_done/', methods=['POST'])
def render_booking_done():
    db_file_booking = database['booking']
    db_file_main = database['main']
    client_name = request.form.get('client_name')
    client_phone = request.form.get('client_phone')
    client_weekday = request.form.get('client_weekday')
    client_time = request.form.get('client_time')
    client_teacher = int(request.form.get('client_teacher'))
    if not validate_username_phone(client_name, client_phone):
        return redirect(f'/booking/{client_teacher}/{client_weekday}/{client_time}/')
    db_booking = load_db_data(db_file_booking)
    teacher = get_teacher_by_id(teacher_list=db_booking, teacher_id=client_teacher)
    if teacher:
        teacher = teacher[0]
        teacher['booking'][client_weekday][client_time] = {'client_name': client_name, 'client_phone': client_phone}
    else:
        db_record = {
            'id': client_teacher,
            'booking': {
                client_weekday: {
                    client_time: {
                        'client_name': client_name,
                        'client_phone': client_phone
                    }
                }
            }
        }
        db_booking.append(db_record)
    db_main_data = load_db_data(db_file_main)
    db_teachers = db_main_data.get('teachers')
    main_db_teacher = get_teacher_by_id(teacher_list=db_teachers, teacher_id=int(client_teacher))[0]
    main_db_teacher['free'][client_weekday][client_time] = False

    dump_db_data(file_path=db_file_main, data=db_main_data)
    dump_db_data(file_path=db_file_booking, data=db_booking)
    return render_template(
        'booking_done.html', weekday=get_week_days()[client_weekday], time=client_time,
        name=client_name, phone=client_phone
    )


def sort_by_key(for_sort, sort_key, reverse=False):
    return sorted(for_sort, key=lambda x: x[sort_key], reverse=reverse)


def validate_username_phone(username, phone):
    if not username or not phone or not re.match(phone_template, phone):
        return False
    return True


def get_teacher_by_id(teacher_list, teacher_id):
    return list(filter(lambda x: x['id'] == teacher_id, teacher_list))


def load_db_data(file_path):
    with open(file_path, 'r', encoding='utf8') as db_file:
        return json.load(db_file)


def dump_db_data(file_path, data):
    with open(file_path, 'w', encoding='utf8') as db_file:
        json.dump(data, db_file, indent=4, ensure_ascii=False)


def get_week_days():
    return {
        'mon': 'Понедельник', 'tue': 'Вторник', 'wed': 'Среда', 'thu': 'Четверг',
        'fri': 'Пятница', 'sat': 'Суббота', 'sun': 'Воскресенье'
    }


if __name__ == '__main__':
    app.run()
