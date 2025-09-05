from datetime import datetime
from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

user_interest = db.Table(
    "user_interest",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("interest_id", db.Integer, db.ForeignKey("interest.id")),
)

user_region = db.Table(
    "user_region",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("region_id", db.Integer, db.ForeignKey("region.id")),
)
