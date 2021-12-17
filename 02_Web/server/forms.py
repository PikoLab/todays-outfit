from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from server.models import *


class RegistrationForm(FlaskForm):
    gender = SelectField('Gender', choices=[('men', 'Man'), ('women', 'Woman')], validators=[DataRequired()])
    uid = StringField('User ID', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_uid(self, uid):
        check_uid = get_user_by_id(uid.data)
        if check_uid:
            raise ValidationError('The User ID is taken. Please try another one.')

    def validate_email(self, email):
        check_email = get_user_by_email(email.data)
        if check_email:
            raise ValidationError('The email is taken. Please try another one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
