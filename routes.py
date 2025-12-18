from ext import app, db
from flask import render_template, request, redirect, url_for, flash
from auth import auth_bp
from models import Trip, User, Review, TripRequest, TripParticipant
from forms import ReviewForm, TripRequestForm, TripForm
from flask_login import current_user, login_required
from os import path, abort
from datetime import timedelta, date, datetime

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
    user_is_participant = TripParticipant.query.filter_by(trip_id=trip.id,
                                                          user_id=current_user.id).first() is not None
    existing_request = TripRequest.query.filter_by(user_id=current_user.id,
                                                   trip_id=trip.id,
                                                   status="pending").first()
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
            flash("Review submitted!")
            return redirect(url_for("trip", trip_id=trip_id))
        else:
            flash("You have already reviewed this trip.")

    is_past = date.today() > trip.end_date
    reviews = Review.query.filter_by(trip_id=trip.id).all()
    return render_template(
        "trip_detail.html",
        trip=trip,
        trip_creator=trip_creator,
        reviews=reviews,
        review_form=review_form,
        is_past=is_past,
        request_form=request_form,
        user_is_creator=user_is_creator,
        user_is_participant=user_is_participant,
        existing_request=existing_request
    )


@app.route("/trip/<int:trip_id>/request", methods=["GET", "POST"])
@login_required
def request_join_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)

    if trip.creator_id == current_user.id:
        abort(403)

    user_is_participant = TripParticipant.query.filter_by(
        trip_id=trip.id,
        user_id=current_user.id
    ).first()

    if user_is_participant:
        flash("You are already a participant.")
        return redirect(url_for("trip", trip_id=trip.id))

    existing_request = TripRequest.query.filter_by(
        trip_id=trip.id,
        user_id=current_user.id
    ).first()

    if existing_request:
        flash("You already sent a request.")
        return redirect(url_for("trip", trip_id=trip.id))

    req = TripRequest(user_id=current_user.id, trip_id=trip.id, status="pending")
    req.create()

    flash("Request sent to trip creator!")
    return redirect(url_for("trip", trip_id=trip.id))


@app.route("/trip-request/<int:request_id>/cancel", methods=["GET", "POST"])
@login_required
def cancel_trip_request(request_id):
    req = TripRequest.query.get(request_id)

    if req.status != "pending":
        flash("You can only cancel pending requests")
        return redirect(url_for("trip", trip_id=req.trip_id))

    req.status = "cancelled"
    req.responded_at = datetime.now()
    req.save()

    flash("Request cancelled")
    return redirect(url_for("trip", trip_id=req.trip_id))


@app.route("/requests")
@login_required
def manage_requests():
    # requests which user made
    my_requests = (
        TripRequest.query.join(Trip)
        .filter(TripRequest.user_id==current_user.id).all()
    )

    # requests of trips user made
    incoming_requests = (
        TripRequest.query.join(Trip)
        .filter(Trip.creator_id==current_user.id)
        .all()
    )

    return render_template("manage_requests.html",
                           my_requests=my_requests,
                           incoming_requests=incoming_requests)

@app.route("/trip-request/<int:request_id>/accept", methods=["GET", "POST"])
@login_required
def accept_request(request_id):
    req = TripRequest.query.get(request_id)

    if req.trip.creator_id != current_user.id:
        abort(403)

    req.status = "accepted"
    req.responded_at = datetime.now()
    trip_participant = TripParticipant(trip_id=req.trip_id, user_id=req.user_id)
    trip_participant.create()

    flash(f"Request accepted for {req.trip.user.name} {req.trip.user.surname}")
    return redirect(url_for("manage_requests"))


@app.route("/trip-request/<int:request_id>/deny", methods=["GET", "POST"])
@login_required
def deny_request(request_id):
    req = TripRequest.query.get(request_id)

    if req.trip.creator_id != current_user.id:
        abort(403)

    req.status = "denied"
    req.save()

    flash(f"Request denied for {req.trip.user.name} {req.trip.user.surname}")
    return redirect(url_for("manage_requests"))

@app.route("/trip/create", methods=["GET", "POST"])
@login_required
def create_trip():
    form = TripForm()
    if form.validate_on_submit():
        trip_img = form.trip_img.data
        directory = path.join(app.root_path, "static", "images", trip_img.filename)
        trip_img.save(directory)
        new_trip = Trip(
            trip_img = trip_img.filename,
            name=form.name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            difficulty=form.difficulty.data,
            description=form.description.data,
            creator_id=current_user.id,
        )
        new_trip.create()

        if current_user.role != "creator":
            current_user.role = "creator"

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