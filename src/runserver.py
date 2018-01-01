#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import application, populate_g

with application.app_context():
    populate_g()

    from web import views
    application.register_blueprint(views.admin_bp)
    application.register_blueprint(views.users_bp)
    application.register_blueprint(views.user_bp)
    application.register_blueprint(views.project_bp)
    application.register_blueprint(views.projects_bp)
    application.register_blueprint(views.organization_bp)
    application.register_blueprint(views.organizations_bp)
    application.register_blueprint(views.service_bp)
    application.register_blueprint(views.services_bp)

    # API v1
    application.register_blueprint(views.api.v1.blueprint_organization)
    application.register_blueprint(views.api.v1.blueprint_project)
    application.register_blueprint(views.api.v1.blueprint_tag)
    application.register_blueprint(views.api.v1.blueprint_user)
    application.register_blueprint(views.api.v1.blueprint_release)
    application.register_blueprint(views.api.v1.blueprint_cve)
    application.register_blueprint(views.api.v1.blueprint_request)


if __name__ == '__main__':
    application.run(host=application.config['HOST'],
                    port=application.config['PORT'])
