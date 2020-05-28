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
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
