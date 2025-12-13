from ext import app
from flask import render_template, request, redirect, url_for, flash
from auth import auth_bp
from models import Trip, User, Review, TripRequest, db
from forms import ReviewForm, TripRequestForm, TripForm
from flask_login import current_user, login_required
from os import path

app.register_blueprint(auth_bp)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/trips", methods=["GET"])
def view_trips():
    trips = Trip.query.all()
    return render_template("trips.html", trips=trips)


@app.route("/profile")
@login_required
def profile():
    trips = Trip.query.filter(Trip.creator_id == current_user.id).all()
    return render_template("profile.html", current_user=current_user, trips=trips)


@app.route("/trip/<int:trip_id>", methods=["GET", "POST"])
@login_required
def trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    trip_creator = User.query.filter_by(id=trip.creator_id).first()
    review_form = ReviewForm()
    request_form = TripRequestForm()
    user_is_creator = trip.creator_id == current_user.id
    # reviews = Review.query.filter(Review.trip_id == trip_id).all()

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
            review.create()
            # db.session.add(review)
            # db.session.commit()
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
                req.create()
                # db.session.add(req)
                # db.session.commit()
                flash("Request sent to trip creator!")
            else:
                flash("You have already requested to join this trip.")
            return redirect(url_for("trip", trip_id=trip_id))

    reviews = Review.query.filter_by(trip_id=trip.id).all()
    return render_template(
        "trip_detail.html",
        trip=trip,
        trip_creator=trip_creator,
        reviews=reviews,
        review_form=review_form,
        request_form=request_form,
        user_is_creator=user_is_creator
    )

@app.route("/trip/<int:trip_id>/requests")
@login_required
def manage_requests(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.creator_id != current_user.id:
        flash("You are not authorized to view this page.")
        return redirect(url_for("trip", trip_id=trip_id))
    requests = TripRequest.query.filter_by(trip_id=trip.id).all()
    return render_template("manage_requests.html", trip=trip, requests=requests)


@app.route("/trip/create", methods=["GET", "POST"])
@login_required
def create_trip():
    form = TripForm()
    if form.validate_on_submit():
        new_trip = Trip(
            name=form.name.data,
            duration=form.duration.data,
            difficulty=form.difficulty.data,
            description=form.description.data,
            creator_id=current_user.id,
        )
        new_trip.create()
        trip_img = form.trip_img.data
        directory = path.join(app.root_path, "static", "images", trip_img.filename)
        trip_img.save(directory)
        new_trip.trip_img = trip_img.filename
        # Automatically assign creator role if not already
        if current_user.role != "creator":
            current_user.role = "creator"
        new_trip.save()
        flash("Trip created successfully! You are now a creator.")
        return redirect(url_for("trip", trip_id=new_trip.id))
    return render_template("create_trip.html", form=form)

@app.route("/delete_trip/<int:trip_id>")
@login_required
def delete_trip(trip_id):
    trip = Trip.query.get(trip_id)
    trip.delete()
    return redirect("/trips")

@app.route("/my_trips")
@login_required
def my_trips():
    user_trips = Trip.query.filter_by(creator_id=current_user.id).all()
    return render_template("trips.html", trips=user_trips)