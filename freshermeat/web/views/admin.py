#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Freshermeat - An open source software directory and release tracker.
# Copyright (C) 2017-2021 Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information: https://sr.ht/~cedric/freshermeat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    current_app,
    flash,
    request,
    abort,
)
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_args
from sqlalchemy import desc
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from werkzeug.security import generate_password_hash

from freshermeat.web.views.common import admin_permission
from freshermeat.bootstrap import db
from freshermeat.web.forms import UserForm
from freshermeat.models import (
    Organization,
    Project,
    Release,
    User,
    Tag,
    Submission,
    License,
    Language,
)

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@login_required
@admin_permission.require(http_exception=403)
def dashboard():
    """Returns a simple dashboard for the administrators. This dashboard
    shows key figures (number of projects, releases, submissions,
    users, etc.) about the platform."""
    nb_projects = Project.query.filter().count()
    nb_releases = Release.query.filter().count()
    nb_organizations = Organization.query.filter().count()
    nb_users = User.query.filter().count()
    nb_admin = User.query.filter(User.is_admin == True).count()
    nb_unique_tags = Tag.query.distinct(Tag.text).count()
    nb_submissions = Submission.query.filter().count()
    nb_pending_submissions = Submission.query.filter(
        Submission.reviewed == False
    ).count()
    return render_template(
        "admin/dashboard.html",
        nb_projects=nb_projects,
        nb_releases=nb_releases,
        nb_users=nb_users,
        nb_admin=nb_admin,
        nb_organizations=nb_organizations,
        nb_unique_tags=nb_unique_tags,
        nb_submissions=nb_submissions,
        nb_pending_submissions=nb_pending_submissions,
    )


@admin_bp.route("/users", methods=["GET"])
@login_required
@admin_permission.require(http_exception=403)
def list_users():
    """Returns to an administrator a page which displays the list of users."""
    users = User.query.all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/user/create", methods=["GET"])
@admin_bp.route("/user/edit/<int:user_id>", methods=["GET"])
@login_required
@admin_permission.require(http_exception=403)
def form_user(user_id=None):
    """Returns a form which let an administrator create/edit users."""
    action = "Add a user"
    head_titles = [action]
    form = UserForm()
    if user_id is None:
        return render_template(
            "admin/edit_user.html", action=action, head_titles=head_titles, form=form
        )

    user = User.query.filter(User.id == user_id).first()
    form = UserForm(obj=user)
    action = "Edit user"
    head_titles = [action]
    head_titles.append(user.login)
    return render_template(
        "admin/edit_user.html",
        action=action,
        head_titles=head_titles,
        form=form,
        user=user,
    )


@admin_bp.route("/user/create", methods=["POST"])
@admin_bp.route("/user/edit/<int:user_id>", methods=["POST"])
@login_required
def process_user_form(user_id=None):
    """Process the form the creation/edition of users."""
    form = UserForm()

    if not form.validate():
        return render_template("admin/edit_user.html", form=form)

    # Edit an existing user
    if user_id is not None:
        user = User.query.filter(User.id == user_id).first()
        form.populate_obj(user)
        if form.password.data:
            user.pwdhash = generate_password_hash(form.password.data)
        db.session.commit()
        flash(
            "User {user_login} successfully updated.".format(
                user_login=form.login.data
            ),
            "success",
        )
        return redirect(url_for("admin_bp.form_user", user_id=user.id))

    # Create a new user
    new_user = User(
        login=form.login.data,
        public_profile=form.public_profile.data,
        is_active=form.is_active.data,
        is_admin=form.is_admin.data,
        is_api=form.is_api.data,
        pwdhash=generate_password_hash(form.password.data),
    )
    db.session.add(new_user)
    db.session.commit()
    flash(
        "User {user_login} successfully created.".format(user_login=new_user.login),
        "success",
    )

    return redirect(url_for("admin_bp.form_user", user_id=new_user.id))


@admin_bp.route("/user/delete/<int:user_id>", methods=["GET"])
@login_required
@admin_permission.require(http_exception=403)
def delete_user(user_id=None):
    """Let an administrator delete a user."""
    pass


@admin_bp.route("/user/toggle/<int:user_id>", methods=["GET"])
@login_required
@admin_permission.require(http_exception=403)
def toggle_user(user_id=None):
    """Let an administrator enable or disable a user."""
    pass


# Flask-Admin views


class SecureView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


menu_link_back_dashboard = MenuLink(name="Dashboard", url="/admin/dashboard")
admin_flask = Admin(
    current_app,
    name="Management of data",
    template_mode="bootstrap3",
    index_view=CustomAdminIndexView(name="Home", url="/admin"),
)
admin_flask.add_view(SecureView(Project, db.session))
admin_flask.add_view(SecureView(Organization, db.session))
admin_flask.add_view(SecureView(License, db.session))
admin_flask.add_view(SecureView(Language, db.session))
admin_flask.add_link(menu_link_back_dashboard)
