from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # asset_type= db.Column(db.String(100))
    ticker = db.Column(db.String(100))
    quantity = db.Column(db.Float)
    date_purchased = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    transaction_type = db.Column(db.String(4))
    total_spent = db.Column(db.Float)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    assets = db.relationship("Asset")
