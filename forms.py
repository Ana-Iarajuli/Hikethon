from flask_wtf import FlaskForm
from wtforms.fields import (StringField, EmailField, PasswordField, IntegerField,
                            DateTimeField, SubmitField, SelectField, TextAreaField)
from wtforms.validators import equal_to, DataRequired, length
from flask_wtf.file import FileField, FileSize, FileAllowed, FileRequired


class RegisterForm(FlaskForm):
    name = StringField("Enter Name")
    surname = StringField("Enter Surname")
    username = StringField("Enter Username", validators=[DataRequired()])
    email = EmailField("JohnDoe@gmail.com", validators=[DataRequired()])
    password = PasswordField("*********", validators=[
        DataRequired(),
        length(min=4, max=24, message="Password length must be between 4-24 characters")
    ])
    confirm_password = PasswordField("Repeat Password", validators=[
        DataRequired(),
        equal_to("password", message="Passwords do not match!")
    ])

    register_btn = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    username = StringField("Enter Username")
    email = EmailField("JohnDoe@gmail.com")
    password = PasswordField("*********")

    login_btn = SubmitField("Login")


class TripForm(FlaskForm):
    name = StringField("Trip Name", validators=[DataRequired()])
    duration = StringField("Duration (e.g. 2 days)", validators=[DataRequired()])
    difficulty = SelectField("Difficulty", choices=[
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('hard', 'Hard'),
        ('extreme', 'Extreme')
    ], validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])

    Submit = SubmitField("Create Trip")