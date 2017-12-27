#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import flash, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import (TextField, TextAreaField, PasswordField, BooleanField,
                     SelectField, SubmitField, validators, HiddenField,
                     SelectMultipleField)
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileField

from lib import misc_utils
from web.models import User, Organization, License


class RedirectForm(FlaskForm):
    """
    Secure back redirects with WTForms.
    """
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = misc_utils.get_redirect_target() or ''

    def redirect(self, endpoint='services', **values):
        if misc_utils.is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = misc_utils.get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class SigninForm(RedirectForm):
    """
    Sign in form.
    """
    login = TextField("Login",
            [validators.Length(min=3, max=30),
            validators.Required("Please enter your login.")])
    password = PasswordField('Password',
            [validators.Required("Please enter a password."),
             validators.Length(min=6, max=100)])
    submit = SubmitField("Log In")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        validated = super().validate()
        user = User.query.filter(User.login == self.login.data).first()
        if not user:
            self.login.errors.append(
                'Impossible to login.')
            validated = False
        else:
            if not user.is_active:
                self.login.errors.append('Impossible to login.')
                validated = False
            if not user.check_password(self.password.data):
                self.password.errors.append('Impossible to login.')
                validated = False
            self.user = user
        return validated


class AddProjectForm(FlaskForm):
    name = TextField("Name", [validators.Optional()])
    description = TextAreaField("Please enter a description",
                            [validators.Optional()])
    short_description = TextField("Short description",
                    [validators.Required("Please enter a short description")])
    website = TextField("Website", [validators.Optional()])
    licenses = SelectMultipleField("Licenses", coerce=int,
                        choices=[(license.id, license.name) for license in
                                    License.query.all()])
    tags = TextField("Tags")
    organization_id = SelectField("Organization", [validators.Optional()],
                                  coerce=int)
    organization_id.choices = [(0, '')]
    organization_id.choices.extend([(org.id, org.name) for org in
                                                Organization.query.all()])
    logo = FileField("Logo")
    enabled = BooleanField("Enabled", default=True)
    submit = SubmitField("Save")


class UserForm(FlaskForm):
    """
    Create or edit a user (for the administrator).
    """
    login = TextField("Login",
            [validators.Length(min=3, max=30),
            validators.Required("Please enter your login.")])
    email = EmailField("Email",
               [validators.Length(max=254)])
    password = PasswordField("Password")
    public_profile = BooleanField("Public profile", default=True)
    is_active = BooleanField("Active", default=True)
    is_admin = BooleanField("Admin", default=False)
    is_api = BooleanField("API", default=False)
    submit = SubmitField("Save")
