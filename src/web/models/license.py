
from datetime import datetime
from bootstrap import db


class License(db.Model):
    """Represent a license.
    https://opensource.org/licenses/alphabetical
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), default='', nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow())
