from datetime import datetime, timezone

import sqlalchemy as sa
from extensions import db
from flask_login import current_user, login_required
from models.post import Post
from models.user import User

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from main.forms import NewPostForm

bp = Blueprint("main", __name__)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route("/", methods=["GET", "POST"])
@login_required
def index_ep():
    form = NewPostForm()

    if form.validate_on_submit():
        post = Post(content=form.content.data, user_id=current_user.id)  # pyright: ignore[reportCallIssue]

        db.session.add(post)
        db.session.commit()

        flash("Post created!")
        return redirect(url_for('main.index_ep'))

    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('main.index_ep', page=posts.next_num) \
        if posts.has_next else None

    prev_url = url_for('main.index_ep', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template("index.html", form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route("/user/<username>")
@login_required
def user_ep(username: str):
    user = db.first_or_404(sa.select(User).where(User.username == username))

    posts = [
        {"author": user, "content": "Test post 1"},
        {"author": user, "content": "Test post 2"},
    ]

    return render_template("profile.html", user=user, posts=posts)
