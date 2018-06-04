from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug import generate_password_hash
from bootstrap import db

from web.models import User
from web.forms import ProfileForm


user_bp = Blueprint('user_bp', __name__, url_prefix='/user')


@user_bp.route('/<string:login>', methods=['GET'])
def get(login=None):
    user = User.query.filter(User.login == login).first()
    return render_template('user.html', user=user)


@user_bp.route('/profile', methods=['GET'])
@login_required
def form():
    user = User.query.filter(User.id == current_user.id).first()
    form = ProfileForm(obj=user)
    form.populate_obj(current_user)
    action = "Edit user"
    head_titles = [action]
    head_titles.append(user.login)
    return render_template('edit_user.html', action=action,
                           head_titles=head_titles,
                           form=form, user=user)


@user_bp.route('/profile', methods=['POST'])
@login_required
def process_form():
    form = ProfileForm()

    if not form.validate():
        return render_template('edit_user.html', form=form)

    user = User.query.filter(User.id == current_user.id).first()
    form.populate_obj(user)
    if form.password.data:
        user.pwdhash = generate_password_hash(form.password.data)
    db.session.commit()
    # flash(User %(user_login)s successfully updated.',
    #         user_login=form.login.data, 'success')
    return redirect(url_for('user_bp.form'))
