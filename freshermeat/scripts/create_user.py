#! /usr/bin/python
# -*- coding:utf-8 -*

from werkzeug.security import generate_password_hash

from freshermeat.models import User
from freshermeat.bootstrap import db


def create_user(login, password, is_admin):
    user = User(
        login=login,
        pwdhash=generate_password_hash(password),
        is_active=True,
        is_admin=is_admin,
    )
    db.session.add(user)
    db.session.commit()
