from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from flask_wtf import FlaskForm
from werkzeug.exceptions import abort
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

from .auth import login_required
from .extensions import get_db, db
from .user.models import Post, User
from .utils import flash_errors

bp = Blueprint('blog', __name__)


class CreateForm(FlaskForm):
    title = StringField(
        "Title", validators=[DataRequired()]
    )
    body = TextAreaField(
        "Content", validators=[]
    )


@bp.route('/')
def index():
    posts = Post.query.all()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = CreateForm(request.form)

    if form.validate_on_submit():
        Post.create(
            title=form.title.data,
            body=form.body.data,
            author_id=g.user.id
        )
        flash("Post created", "success")
        return redirect(url_for('blog.index'))
    else:
        flash_errors(form)

    return render_template('blog/create.html', form=form)


def get_post(id, check_author=True):
    post = Post.get_by_id(id)

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post.author != g.user:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    form = CreateForm(request.form)

    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data

        db.session.commit()

        flash(f"Post updated to {post.body}", "success")
        return redirect(url_for('blog.index'))
    else:
        form.title.data = post.title
        form.body.data = post.body

        flash_errors(form)

    return render_template('blog/update.html', form=form, post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
