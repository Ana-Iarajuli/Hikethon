from datetime import datetime
from ext import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates


class BaseModel:
    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save():
        db.session.commit()


class User(db.Model, BaseModel, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    surname = db.Column(db.String(), nullable=False)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, name, surname, username, email, password, role="Guest"):
        self.name = name
        self.surname = surname
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def check_email(email):
        return User.query.filter(User.email==email).first()
    
    @staticmethod
    def check_username(username):
        return User.query.filter(User.username==username).first()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Trip(db.Model, BaseModel):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False) # It will be calculated automatically
    difficulty = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trip_img = db.Column(db.String(100), nullable=False)

    user = db.relationship("User", backref="created_trips")

    @validates("start_date", "end_date")
    def validate_dates(self, key, value):
        start_date = value if key == "start_date" else self.start_date
        end_date = value if key == "end_date" else self.end_date

        if start_date and end_date:
            if end_date < start_date:
                raise ValueError("End date cannot be before start date")
            self.duration = (end_date - start_date).days + 1

        return value


class Review(db.Model, BaseModel):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # constraint: one user - one review
    __table_args__ = (
        db.UniqueConstraint("user_id", "trip_id", name="uq_review_user_trip"),
    )

    # Relationships
    user = db.relationship('User', backref="reviews", lazy=True)
    trip = db.relationship('Trip', backref="reviews", lazy=True)


class TripRequest(db.Model, BaseModel):
    __tablename__ = "trip_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # pending, cancelled (by user); accepted, rejected (by trip creator)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)

    user = db.relationship('User', backref="trip_requests", lazy=True) # creator of the trip
    trip = db.relationship('Trip', backref="requests", lazy=True)


class TripParticipant(db.Model, BaseModel):
    __tablename__ = "trip_participants"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)

    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "trip_id", name="uq_user_trip"),
    )

    user = db.relationship("User", backref="participations")
    trip = db.relationship("Trip", backref="participants")