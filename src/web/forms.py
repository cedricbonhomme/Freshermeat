#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import flash, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import (TextField, TextAreaField, PasswordField, BooleanField,
                     SelectField, SubmitField, validators, HiddenField)

from lib import misc_utils
from web.models import User, Organization


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
    email = TextField("Email",
            [validators.Length(min=3, max=35),
            validators.Required("Please enter your email address.")])
    password = PasswordField('Password',
            [validators.Required("Please enter a password."),
             validators.Length(min=6, max=100)])
    submit = SubmitField("Log In")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        validated = super().validate()
        user = User.query.filter(User.email == self.email.data).first()
        if not user:
            self.email.errors.append(
                'Wrong email address or password')
            validated = False
        else:
            if not user.is_active:
                self.email_or_nickmane.errors.append(
                    'Wrong email address or password')
                validated = False
            if not user.check_password(self.password.data):
                self.password.errors.append('Wrong email address or password')
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
    organization_id = SelectField("Organization", [validators.Optional()],
                                  coerce=int)
    organization_id.choices = [(org.id, org.name) for org in Organization.query.all()]
    enabled = BooleanField("Enabled", default=True)
    submit = SubmitField("Save")
