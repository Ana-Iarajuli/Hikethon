from ext import app
from flask import render_template, request, redirect, url_for, flash
from auth import auth_bp
from models import Trip, Review, TripRequest, db
from forms import ReviewForm, TripRequestForm, TripForm
from flask_login import current_user, login_required

app.register_blueprint(auth_bp)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/trips", methods=["GET"])
def view_trips():
    return render_template("trips.html")

@app.route("/profile")
def profile():
    pass


@app.route("/trip/<int:trip_id>", methods=["GET", "POST"])
@login_required
def trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    review_form = ReviewForm()
    request_form = TripRequestForm()
    user_is_creator = trip.created_by == current_user.id

    # Handle review submission
    if review_form.validate_on_submit() and review_form.submit.data:
        already_reviewed = Review.query.filter_by(user_id=current_user.id, trip_id=trip.id).first()
        if not already_reviewed:
            review = Review(
                user_id=current_user.id,
                trip_id=trip.id,
                rating=int(review_form.rating.data),
                comment=review_form.comment.data
            )
            db.session.add(review)
            db.session.commit()
            flash("Review submitted!")
            return redirect(url_for("trip", trip_id=trip_id))
        else:
            flash("You have already reviewed this trip.")

    # Handle trip request
    if request_form.validate_on_submit() and request_form.submit.data:
        if not user_is_creator:
            existing_request = TripRequest.query.filter_by(user_id=current_user.id, trip_id=trip.id).first()
            if not existing_request:
                req = TripRequest(user_id=current_user.id, trip_id=trip.id)
                db.session.add(req)
                db.session.commit()
                flash("Request sent to trip creator!")
            else:
                flash("You have already requested to join this trip.")
            return redirect(url_for("trip", trip_id=trip_id))

    reviews = Review.query.filter_by(trip_id=trip.id).all()
    return render_template(
        "trip_detail.html",
        trip=trip,
        reviews=reviews,
        review_form=review_form,
        request_form=request_form,
        user_is_creator=user_is_creator
    )

@app.route("/trip/<int:trip_id>/requests")
@login_required
def manage_requests(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.created_by != current_user.id:
        flash("You are not authorized to view this page.")
        return redirect(url_for("trip", trip_id=trip_id))
    requests = TripRequest.query.filter_by(trip_id=trip.id).all()
    return render_template("manage_requests.html", trip=trip, requests=requests)


@app.route("/trip/create", methods=["GET", "POST"])
@login_required
def create_trip():
    form = TripForm()
    if form.validate_on_submit():
        trip = Trip(
            name=form.name.data,
            duration=form.duration.data,
            difficulty=form.difficulty.data,
            description=form.description.data,
            created_by=current_user.id
        )
        db.session.add(trip)
        # Automatically assign creator role if not already
        if current_user.role != "creator":
            current_user.role = "creator"
        db.session.commit()
        flash("Trip created successfully! You are now a creator.")
        return redirect(url_for("trip", trip_id=trip.id))
    return render_template("create_trip.html", form=form)

