from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, HiddenField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError


class PhoneValidator(Length):
    def __call__(self, form, field):
        super().__call__(form, field)
        if not field.data[1:].isdigit() or not (field.data[0] == '+' or field.data[0].isdigit()):
            message = self.message
            if message is None:
                message = field.gettext('Phone should content only digits and start with + or digit')
            raise ValidationError(message)


class RequestForm(FlaskForm):
    goal_id = RadioField('Какая цель занятий?', choices=[], default='1')
    free_time = RadioField(
        'Сколько времени есть?', choices=[
            ('1-2', '1-2 часа в неделю'), ('3-5', '3-5 часов в неделю'),
            ('5-7', '5-7 часов в неделю'), ('7-10', '7-10 часов в неделю')
        ], default='3-5')
    client_name = StringField('Вас зовут', [InputRequired()])
    client_phone = StringField('Ваш телефон', [InputRequired(), PhoneValidator(min=11, max=12)])
    submit = SubmitField("Найдите мне преподавателя")


class BookingForm(FlaskForm):
    lesson_id = HiddenField('lesson_id')
    client_name = StringField('Вас зовут', [InputRequired()])
    client_phone = StringField('Ваш телефон', [InputRequired(), PhoneValidator(min=11, max=12)])
    submit = SubmitField('Записаться на пробный урок')


