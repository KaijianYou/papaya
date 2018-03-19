from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import gettext as _

from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegisterForm, ChangePasswordForm, \
    ResetPasswordForm, ResetPasswordRequestForm, ChangeEmailForm
from models.user import User
from utils.email_util import EmailUtil
from utils.request_util import is_safe_url


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_visited()
        if (not current_user.confirmed and
                request.endpoint and
                not request.endpoint.startswith('auth.') and
                request.endpoint != 'static'):
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirmed')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    EmailUtil.send_confirm_email(user=current_user, token=token)
    flash(_('A new confirmation email has been sent to you by email'), 'info')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()
        EmailUtil.send_confirm_email(user=user, token=token)
        flash(_('A confirmation email has been sent to you by email'), 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(_('You have confirmed your account. Thanks!'), 'success')
        EmailUtil.send_new_user_email(user=current_user)
    else:
        flash(_('The confirmation link is invalid or has expired'), 'warning')
    return redirect(url_for('main.index'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(_('Logged in successfully'), 'success')
            next_url = request.args.get('next')
            if not is_safe_url(next_url):
                return abort(400)
            return redirect(next_url or url_for('main.index'))
        flash(_('Invalid email or password'), 'warning')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out'), 'info')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash(_('Your password has been updated'), 'success')
            return redirect(url_for('main.index'))
        else:
            flash(_('Invalid password'), 'warning')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = user.generate_password_reset_token()
            EmailUtil.send_reset_password_email(user=user,
                                                token=token,
                                                next=request.args.get(next))
            flash(_('An email with instructions to reset '
                    'your password has been sent to you'),
                  'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash(_('Your password has been updated'), 'success')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            # 将新设的邮箱账号保存到令牌中
            token = current_user.generate_email_change_token(new_email)
            EmailUtil.send_change_email_email(new_email,
                                              user=current_user,
                                              token=token,
                                              next=request.args.get(next))
            flash(_('An email with instructions to confirm your '
                    'new email address has been sent to you.'), 'info')
            return redirect(url_for('main.index'))
        else:
            flash(_('Invalid email or password'), 'warning')
    return render_template('/auth/change_email.html', form=form)


@auth.route('/change-email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash(_('Your email address has been updated'), 'success')
    else:
        flash(_('Invalid request'), '')
    return redirect(url_for('main.index'))
