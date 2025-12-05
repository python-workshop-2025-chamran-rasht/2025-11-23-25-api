from urllib.parse import urlsplit

import jwt
import sqlalchemy as sa
from extensions import db
from flask_login import (
    current_user,
    login_user,
    logout_user,
)
from models.user import User

from auth.email import send_password_reset_email
from auth.forms import LoginForm, PasswordChangeForm, PasswordResetForm, SignupForm
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

bp = Blueprint("auth", __name__)


@bp.route("/logout")
def logout_ep():
    logout_user()
    return redirect(url_for("main.index_ep"))


@bp.route("/login", methods=["GET", "POST"])
def login_ep():
    next_page = request.args.get("next")

    if not next_page or urlsplit(next_page).netloc != "":
        next_page = url_for("main.index_ep")

    if current_user.is_authenticated:
        return redirect(next_page)

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.Select(User).where(User.username == form.username.data)
        )

        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(next_page)

        flash("Invalid username or password")

    return render_template("auth/login.html", form=form)


@bp.route("/signup", methods=["GET", "POST"])
def signup_ep():
    form = SignupForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)  # pyright: ignore[reportCallIssue]

        assert form.password.data is not None
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("main.index_ep"))

    return render_template("auth/signup.html", form=form)


@bp.route("/password-reset", methods=["GET", "POST"])
def reset_passwd_ep():
    form = PasswordResetForm()

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))

        if user:
            send_password_reset_email(user)

        flash("Check your email for password reset instructions")

    return render_template("auth/reset_password.html", form=form)


@bp.route("/password-reset/<token>", methods=["GET", "POST"])
def change_passwd_ep(token):
    try:
        user_id = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )["user"]
    except:  # noqa: E722
        return redirect(url_for("main.index_ep"))

    user = db.session.get(User, user_id)
    assert user

    form = PasswordChangeForm()

    if form.validate_on_submit():
        assert form.password.data
        user.set_password(form.password.data)
        db.session.commit()

        flash("Your password was changed")
        return redirect(url_for("auth.login_ep"))

    return render_template("auth/change_password.html", form=form)
