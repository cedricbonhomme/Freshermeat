#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
from flask_login import current_user
from flask_restless import ProcessingException
from werkzeug.exceptions import NotFound
from web.views.common import login_user_bundle

url_prefix = '/api/v1'

def auth_func(*args, **kw):
    if request.authorization:
        user = None
        try:
            user = User.query.filter(User.email == request.authorization.email).first()
        except NotFound:
            raise ProcessingException("Couldn't authenticate your user",
                                        code=401)
        if not user.check_password(user, request.authorization.password):
            raise ProcessingException("Couldn't authenticate your user",
                                        code=401)
        if not user.is_active:
            raise ProcessingException("User is desactivated", code=401)
        login_user_bundle(user)
    if not current_user.is_authenticated:
        raise ProcessingException(description='Not authenticated!', code=401)

class AbstractProcessor():
    """Abstract processors for the Web services.
    """

    def is_authorized(self, user, obj):
        if user.id != obj.user_id:
            raise ProcessingException(description='Not Authorized', code=401)

    def get_single_preprocessor(self, instance_id=None, **kw):
        # Check if the user is authorized to modify the specified
        # instance of the model.
        pass

    def get_many_preprocessor(self, search_params=None, **kw):
        """Accepts a single argument, `search_params`, which is a dictionary
        containing the search parameters for the request.
        """
        filt = dict(name="user_id",
                    op="eq",
                    val=current_user.id)

        # Check if there are any filters there already.
        if "filters" not in search_params:
          search_params["filters"] = []

        search_params["filters"].append(filt)

    def post_preprocessor(self, data=None, **kw):
        pass

    def put_single_preprocessor(instance_id=None, data=None, **kw):
        """Accepts two arguments, `instance_id`, the primary key of the
        instance of the model to patch, and `data`, the dictionary of fields
        to change on the instance.
        """
        pass

    def put_many_preprocessor(search_params=None, data=None, **kw):
        """Accepts two arguments: `search_params`, which is a dictionary
        containing the search parameters for the request, and `data`, which
        is a dictionary representing the fields to change on the matching
        instances and the values to which they will be set.
        """
        filt = dict(name="user_id",
                    op="eq",
                    val=current_user.id)

        # Check if there are any filters there already.
        if "filters" not in search_params:
          search_params["filters"] = []

        search_params["filters"].append(filt)

    def delete_preprocessor(self, instance_id=None, **kw):
        pass
