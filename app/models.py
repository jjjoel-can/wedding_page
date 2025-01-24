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
    service_type = db.Column(db.String(50), nullable=False)
    price_range = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Vendor {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "service_type": self.service_type,
            "price_range": self.price_range
        }

