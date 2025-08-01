from ext import app
from flask import render_template
from auth import auth_bp
from models import Trip

app.register_blueprint(auth_bp)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/routes")
def view_routes():
    return render_template("routes.html")

@app.route("/profile")
def profile():
    pass


@app.route("/route/<int:route_id>")
def route():
    pass

