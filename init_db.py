from ext import app, db
from models import User, Trip, TripParticipant, TripRequest, Review

with app.app_context():
    db.drop_all()
    db.create_all()

    admin_user = User(name="admin", surname="admin",
                      username="admin", email="admin@test.com", password="admin123",
                      role="Admin")

    admin_user.create()
