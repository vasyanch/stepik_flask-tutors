import json
import re

from random import randint
from flask import Flask, render_template, request, redirect, url_for


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
    teacher = get_teacher_by_id(teacher_list=db_main_data.get('teachers'), teacher_id=int(teacher_id))
    week_days = get_week_days()
    goals = db_main_data.get('goals')
    return render_template('profile.html', teacher=teacher, week_days=week_days, goals=goals)


@app.route('/request/', methods=['POST', 'GET'])
def render_request():
    error = ''
    if request.method == 'POST':
        db_file_request = database['request']
        db_file_main = database['main']
        client_name = request.form.get('client_name')
        client_phone = request.form.get('client_phone')
        goal = request.form.get('goal')
        free_time = request.form.get('time')
        if not validate_username_phone(client_name, client_phone):
            error = "Invalid or empty name or phone"
            return render_template('request.html', error=error)

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
        return redirect(
            url_for(
                '.render_request_done', goal=goals.get(goal)[0], free_time=free_time,
                name=client_name, phone=client_phone
            )
        )
    return render_template('request.html', error=error)


@app.route('/request_done/')
def render_request_done():
    return render_template(
        'request_done.html', goal=request.args['goal'], free_time=request.args['free_time'],
        name=request.args['name'], phone=request.args['phone']
    )


@app.route('/booking/<teacher_id>/<week_day>/<day_time>/', methods=['POST', 'GET'])
def render_booking(teacher_id, week_day, day_time):
    error = ''
    db_file_booking = database['booking']
    db_file_main = database['main']
    db_main_data = load_db_data(db_file_main)
    all_teachers = db_main_data.get('teachers')
    main_db_teacher = get_teacher_by_id(teacher_list=all_teachers, teacher_id=int(teacher_id))
    week_days = get_week_days()
    if request.method == 'POST':
        client_name = request.form.get('client_name')
        client_phone = request.form.get('client_phone')
        if not validate_username_phone(client_name, client_phone):
            error = "Invalid or empty name or phone"
            return render_template(
                'booking.html', teacher=main_db_teacher, week_day=week_day, day_time=day_time,
                week_days=week_days, error=error
            )
        db_booking = load_db_data(db_file_booking)
        booking_teacher = get_teacher_by_id(teacher_list=db_booking, teacher_id=teacher_id)
        if booking_teacher:
            if not booking_teacher['booking'].get(week_day):
                booking_teacher['booking'][week_day] = {}
            booking_teacher['booking'][week_day][day_time] = \
                {'client_name': client_name, 'client_phone': client_phone}
        else:
            db_record = {
                'id': teacher_id,
                'booking': {
                    week_day: {
                        day_time: {
                            'client_name': client_name,
                            'client_phone': client_phone
                        }
                    }
                }
            }
            db_booking.append(db_record)
        main_db_teacher['free'][week_day][day_time] = False

        dump_db_data(file_path=db_file_main, data=db_main_data)
        dump_db_data(file_path=db_file_booking, data=db_booking)
        return redirect(
            url_for(
                '.render_booking_done', week_day=week_day, time=day_time, client_name=client_name,
                client_phone=client_phone
            )
        )
    return render_template(
        'booking.html', teacher=main_db_teacher, week_day=week_day, day_time=day_time, week_days=week_days, error=error
    )


@app.route('/booking_done/')
def render_booking_done():
    return render_template(
        'booking_done.html', weekday=get_week_days()[request.args['week_day']], time=request.args['time'],
        name=request.args['client_name'], phone=request.args['client_phone']
    )


def sort_by_key(for_sort, sort_key, reverse=False):
    return sorted(for_sort, key=lambda x: x[sort_key], reverse=reverse)


def validate_username_phone(username, phone):
    if not username or not phone or not re.match(phone_template, phone):
        return False
    return True


def get_teacher_by_id(teacher_list, teacher_id):
    answer_list = list(filter(lambda x: x['id'] == teacher_id, teacher_list))
    return answer_list[0] if answer_list else None


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
