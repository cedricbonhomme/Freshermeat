#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Freshermeat - An open source software directory and release tracker.
# Copyright (C) 2017-2018  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://github.com/cedricbonhomme/Freshermeat
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
from flask import request
from flask_login import current_user
from flask_restless import ProcessingException

import lib.checks
from bootstrap import db
from notifications.notifications import new_request_notification
from web.views.common import login_user_bundle
from web.models import User, Service, Request

logger = logging.getLogger(__name__)

def auth_func(*args, **kw):
    print('auth_func')
    if request.authorization:
        user = User.query.filter(User.login == request.authorization.username).first()
        if not user:
            raise ProcessingException("Couldn't authenticate your user",
                                      code=401)
        if not user.check_password(request.authorization.password):
            raise ProcessingException("Couldn't authenticate your user",
                                      code=401)
        if not user.is_active:
            raise ProcessingException("Couldn't authenticate your user", code=401)
        login_user_bundle(user)
    if not current_user.is_authenticated:
        raise ProcessingException(description='Not authenticated!', code=401)


def post_preprocessor(data=None, **kw):
    """Accepts a single argument, `data`, which is the dictionary of
    fields to set on the new instance of the model.

    Checks if the service corresponding to user's request is enabled.
    Before the creation of a new request, the content submited by the user
    is checked against the appropriate functions.
    """
    service_id = data['service_id']
    service = Service.query.filter(Service.id == service_id).first()
    if not service.service_enabled:
        raise ProcessingException(
            "Service currently not available.", code=422)
    checks = []
    for info in service.required_informations:
        for check in info.get('checks', []):
            try:
                check_function = getattr(lib.checks, check)
            except AttributeError:
                # the check 'check' do not exists
                continue
            try:
                # 'parameter' is the content submitted by the user that we want
                # to check against check_function
                parameter = data['required_informations'][info['name']]
            except KeyError:
                # a non-required information that was not submitted by the user
                continue
            checks.append(check_function(parameter))
    if not all(checks):
        logger.info('Unsuccessful request for {}'.format(service.name))
        raise ProcessingException(
            "The values you submitted do not pass all checks!", code=422)
    logger.info('New request for {}'.format(service.name))


def post_postprocessor(result=None, **kw):
    """Accepts a single argument, `result`, which is the dictionary
    representation of the created instance of the model.

    Right after the creation a new request, a notification is sent to the
    service responsible.
    """
    new_request = None
    try:
        new_request = Request.query.filter(Request.id == result['id']).first()
    except Exception as e:
        print(e)

    if new_request:
        # send the notification...
        try:
            new_request_notification(new_request)
            new_request.notification_sent = True
            db.session.commit()
            logger.info('Request notifiation sent (request {})'.format(new_request.id))
        except Exception as e:
            logger.exception('request POST post-processor: ' + str(e))
