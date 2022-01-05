from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func 

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    asset_type = db.Column(db.String(100))
    ticker = db.Column(db.String(10000))
    quantity = db.Column(db.Integer)
    date_purchased = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def to_dict(self):
        return {
            'name': self.name,
            'asset_type': self.asset_type,
            'ticker': self.ticker, 
            'quantity': self.quantity,
            'date_purchased': self.date_purchased
        }



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique =True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    assets = db.relationship('Asset')