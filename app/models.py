'''
Database
'''

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # SQLAlchemy instance to handle the database

class Vendor(db.Model):
    __tablename__ = "vendors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=True) # added country
    service_type = db.Column(db.String(50), nullable=False)
    price_range = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(200), nullable=True)  # Physical address
    city = db.Column(db.String(50), nullable=True)  # City or location
    contact = db.Column(db.String(100), nullable=True)  # Email/phone/social media
    hours = db.Column(db.String(100), nullable=True)  # Operating hours
    picture_url = db.Column(db.String(200), nullable=True)  # URL or path to the picture

    def __repr__(self):
        '''return string representation of the object
        '''
        return f"<Vendor {self.name}>"

    def to_dict(self):
        '''return attributes ad dictionary
        '''
        return {
            "id": self.id,
            "name": self.name,
            "service_type": self.service_type,
            "price_range": self.price_range,
            "address": self.address,
            "country": self.country,
            "city": self.city,
            "contact": self.contact,
            "hours": self.hours,
            "picture_url": self.picture_url
        }