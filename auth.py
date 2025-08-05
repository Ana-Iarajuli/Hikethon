from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if not (User.check_username(form.username.data) and User.check_email(form.email.data)):
            new_user = User(name=form.name.data,
                            surname=form.surname.data,
                            username=form.username.data,
                            email=form.email.data,
                            password=form.password.data)
            new_user.create()
            return redirect(url_for("auth.login"))
        return "email or username already exists"
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        checked_password = user.check_password(form.password.data)
        if user and checked_password:
            login_user(user)
            flash("You are logged in!")
            return redirect(url_for("index"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))