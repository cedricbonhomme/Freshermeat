import logging
from flask import render_template, flash, url_for, redirect, current_app


logger = logging.getLogger(__name__)


@current_app.errorhandler(401)
def authentication_required(error):
    flash('Authentication required.', 'info')
    return redirect(url_for('login'))


@current_app.errorhandler(403)
def authentication_failed(error):
    flash('Forbidden.', 'danger')
    return redirect(url_for('login'))


@current_app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@current_app.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 500


@current_app.errorhandler(AssertionError)
def handle_sqlalchemy_assertion_error(error):
    return error.args[0], 400


@current_app.route('/', methods=['GET'])
def services():
    return render_template('services.html')


@current_app.route('/service', methods=['GET'])
def service():
    return render_template('service.html')
