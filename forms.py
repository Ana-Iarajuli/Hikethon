from flask_wtf import FlaskForm
from wtforms.fields import (StringField, EmailField, PasswordField, IntegerField,
                            DateTimeField, SubmitField, SelectField, TextAreaField)
from wtforms.validators import equal_to, DataRequired, length
from flask_wtf.file import FileField, FileSize, FileAllowed, FileRequired
from wtforms import RadioField


class RegisterForm(FlaskForm):
    name = StringField("Enter Name")
    surname = StringField("Enter Surname")
    username = StringField("Enter Username", validators=[DataRequired()])
    email = EmailField("JohnDoe@gmail.com", validators=[DataRequired()])
    password = PasswordField("Password", validators=[
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
    email = EmailField("Email")
    password = PasswordField("Password")

    login_btn = SubmitField("Sign In")


class TripForm(FlaskForm):
    trip_img = FileField("Upload Trip Photo", validators=[
        FileRequired(message="You must upload photo"),
        FileSize(1024 * 1024 * 5),
        FileAllowed(["jpg", "png", "jpeg", "JPG"], message="Only jpg/png files are allowed")
    ])
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


class ReviewForm(FlaskForm):
    rating = RadioField("Rating", choices=[(str(i), str(i)) for i in range(1, 6)], validators=[DataRequired()])
    comment = TextAreaField("Comment", validators=[length(max=500)])
    submit = SubmitField("Submit Review")


class TripRequestForm(FlaskForm):
    submit = SubmitField("Request to Join")