from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


association_table = db.Table(
    "association_teacher_goals", db.metadata,
    db.Column('Teacher', db.Integer, db.ForeignKey('teachers.id'), nullable=False),
    db.Column('Goal', db.Integer, db.ForeignKey('goals.id'), nullable=False)
)


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    about = db.Column(db.Text, nullable=False)
    picture = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Float)
    price = db.Column(db.Integer, nullable=False)
    goals = db.relationship("Goal", secondary=association_table, back_populates='teachers')
    lessons = db.relationship('Lesson', back_populates='teacher')


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(), nullable=False, unique=True)
    emoji = db.Column(db.String(), nullable=False)
    teachers = db.relationship("Teacher", secondary=association_table, back_populates="goals")
    requests = db.relationship('RequestLesson', back_populates='goal')


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(), nullable=False)
    client_phone = db.Column(db.String(), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    lesson = db.relationship('Lesson', back_populates='booking')


class RequestLesson(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False)
    goal = db.relationship('Goal', back_populates='requests')
    free_time = db.Column(db.String(), nullable=False)
    client_name = db.Column(db.String(), nullable=False)
    client_phone = db.Column(db.String(), nullable=False)


class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    teacher = db.relationship('Teacher', back_populates='lessons')
    day_name_id = db.Column(db.Integer, db.ForeignKey('weekdays.id'), nullable=False)
    day_name = db.relationship('WeekDay', back_populates='lessons')
    time_id = db.Column(db.Integer, db.ForeignKey('times.id'), nullable=False)
    time = db.relationship('Time', back_populates='lessons')
    booking = db.relationship('Booking', uselist=False, back_populates='lesson')
    status = db.Column(db.Boolean, nullable=False)


class WeekDay(db.Model):
    __tablename__ = 'weekdays'
    id = db.Column(db.Integer, primary_key=True)
    day_name = db.Column(db.String(11), nullable=False, unique=True)
    lessons = db.relationship('Lesson', back_populates='day_name')


class Time(db.Model):
    __tablename__ = 'times'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Time, nullable=False, unique=True)
    lessons = db.relationship('Lesson', back_populates='time')

    def get_str_time(self):
        return self.time.strftime('%H:%M')
