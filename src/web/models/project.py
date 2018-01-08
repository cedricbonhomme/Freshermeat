
from datetime import datetime
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import validates
from sqlalchemy import event

from bootstrap import db


association_table = db.Table('association_projects_licenses', db.metadata,
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('license_id', db.Integer, db.ForeignKey('license.id'))
)


class Project(db.Model):
    """Represent a project.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    short_description = db.Column(db.String(300), unique=True)
    description = db.Column(db.String(), unique=True)
    website = db.Column(db.String())
    enabled = db.Column(db.Boolean(), default=True)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow())

    # if cve_vendor is the empty string use the parent property
    # (organization.cve_vendor)
    cve_vendor = db.Column(db.String(), default='')
    cve_product = db.Column(db.String(), unique=True, nullable=False)

    automatic_release_tracking = db.Column(db.String())

    notification_email = db.Column(db.String(), default='')
    required_informations = db.Column(JSON, default=None)

    # foreign keys
    organization_id = db.Column(db.Integer(), db.ForeignKey('organization.id'))
    manager_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    icon_url = db.Column(db.String(), db.ForeignKey('icon.url'), default=None)

    # relationships
    code_locations = db.relationship('Code', backref='project', lazy='dynamic',
                               cascade='all,delete-orphan')
    tag_objs = db.relationship('Tag', back_populates='project',
                               cascade='all,delete-orphan',
                               lazy=False,
                               foreign_keys='[Tag.project_id]')
    tags = association_proxy('tag_objs', 'text')
    licenses = db.relationship("License",
                            secondary=lambda: association_table,
                            backref="projects")
    cves = db.relationship('CVE', backref='project', lazy='dynamic',
                               cascade='all,delete-orphan')
    releases = db.relationship('Release', backref='project', lazy='dynamic',
                               cascade='all,delete-orphan')

    @validates('name')
    def validates_name(self, key, value):
        assert len(value) <= 100, \
            AssertionError("maximum length for name: 100")
        return value.replace(' ', '').strip()

    def __repr__(self):
        return '<Name %r>' % (self.name)


@event.listens_for(Project, 'before_insert')
def page_defaults(mapper, configuration, target):
    # `cve_product` defaults to `name`
    if not target.cve_product:
        target.cve_product = target.name.lower()


@event.listens_for(Project, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """Event listener that runs before a record is updated, and sets the
    last_updated field accordingly.
    """
    target.last_updated = datetime.utcnow()
