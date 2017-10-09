
from datetime import datetime
from flask_login import UserMixin
from werkzeug import check_password_hash
from sqlalchemy.dialects.postgresql import JSON

from bootstrap import db

class Request(db.Model, UserMixin):
    """Represent a request.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False)
    firstname = db.Column(db.String(), default='')
    lastname = db.Column(db.String(), default='')
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    required_informations = db.Column(JSON)

    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'))

    # Relationship
    service = db.relationship('Service', backref="requests")
