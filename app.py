import os

from flask import Flask
from flask import render_template, request
from flask_migrate import Migrate

from forms import RequestForm, BookingForm
from models import Teacher, Goal, Lesson, WeekDay, RequestLesson, Booking
from models import db

app = Flask(__name__)
app.secret_key = os.environ.get('STEPIK_TUTORS_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/all')
@app.route('/')
def render_index():
    if request.path == '/all':
        teachers = Teacher.query.order_by(Teacher.rating.desc()).all()
    else:
        teachers = Teacher.query.order_by(db.func.random()).limit(6).all()
    goals = Goal.query.order_by(Goal.id).all()
    return render_template('index.html', teachers=teachers, goals=goals)


@app.route('/goals/<goal_id>/')
def render_goal(goal_id):
    goal_id = int(goal_id)
    goal_teachers = Teacher.query.filter(Goal.id == goal_id).order_by(Teacher.rating.desc()).all()
    goal = Goal.query.get_or_404(goal_id)
    return render_template('goal.html', goal=goal, teachers=goal_teachers)


@app.route('/profiles/<teacher_id>/')
def render_profile(teacher_id):
    teacher_id = int(teacher_id)
    teacher = Teacher.query.get_or_404(teacher_id)
    free_times = Lesson.query.filter(db.and_(Lesson.teacher_id == teacher_id, Lesson.status == True)).\
        order_by(Lesson.day_name_id, Lesson.time_id)
    dict_days_free_times = {
        day.id: {'day_name': day.day_name, 'free_time': [], 'lesson_id': None}
        for day in WeekDay.query.order_by(WeekDay.id)
    }
    for record in free_times:
        dict_days_free_times[record.day_name_id]['free_time'].append(record.time.get_str_time())
        dict_days_free_times[record.day_name_id]['lesson_id'] = record.id
    list_days_free_times = sorted(list(dict_days_free_times.items()), key=lambda x: x[0])
    return render_template('profile.html', teacher=teacher, free_times=list_days_free_times)


@app.route('/request/', methods=['POST', 'GET'])
def render_request():
    form = RequestForm()
    goals = Goal.query.order_by(Goal.id)
    form.goal_id.choices = [(str(goal.id), goal.value) for goal in goals]
    goals = Goal.query.order_by(Goal.id).all()
    if request.method == 'POST' and form.validate_on_submit():
        lesson_request = RequestLesson()
        form.populate_obj(lesson_request)
        db.session.add(lesson_request)
        db.session.commit()
        client_name = form.client_name.data
        client_phone = form.client_phone.data
        goal = list(filter(lambda x: x.id == int(form.goal_id.data), goals))[0].value
        free_time = form.free_time.data
        free_time = free_time + ' часа в неделю' if free_time == '1-2' else free_time + ' часов в неделю'
        return render_template(
            'request_done.html', goal=goal, free_time=free_time, name=client_name, phone=client_phone
        )
    return render_template('request.html', form=form)


@app.route('/booking/<lesson_id>/', methods=['POST', 'GET'])
def render_booking(lesson_id):
    error = ''
    form = BookingForm()
    lesson_id = int(lesson_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    week_day = lesson.day_name.day_name
    _time = lesson.time.get_str_time()
    teacher = lesson.teacher
    if not lesson.status:
        error = f'Извините, у {teacher.name}  в  {week_day.lower()} {_time} нет свободного времени, ' \
                f'пожалуйста выберите другое время'
    if request.method == 'POST' and form.validate_on_submit() and error == '':
        form.lesson_id.data = int(lesson_id)
        booking = Booking()
        form.populate_obj(booking)
        client_name, client_phone = form.client_name.data, form.client_phone.data
        lesson.status = False
        db.session.add_all([lesson, booking])
        db.session.commit()
        return render_template(
            'booking_done.html', week_day=week_day, day_time=_time, name=client_name, phone=client_phone
        )
    form.lesson_id.data = str(lesson_id)
    return render_template(
        'booking.html', teacher=teacher, lesson_id=lesson_id, week_day=week_day, day_time=_time, error=error, form=form
    )


if __name__ == '__main__':
    app.run()
