import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, Length

from .extensions import get_db
from .user.models import User
from .utils import flash_errors

bp = Blueprint('auth', __name__, url_prefix='/auth')


class RegisterForm(FlaskForm):
    """Register form."""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=40)]
    )
    email = StringField(
        "Email", validators=[DataRequired(), Email(), Length(min=6, max=150)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=40)]
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Username already registered")
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=40)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=40)]
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        self.user = User.query.filter_by(username=self.username.data).first()

        if not self.user:
            self.user.errors.append("No such user")
            return False

        if not check_password_hash(self.user.password, self.password.data):
            self.password.errors.append("Incorrect password")
            return False

        return True


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register new user."""
    form = RegisterForm(request.form)

    if form.validate_on_submit():
        User.create(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
        )
        flash("Thank you for registering. You can now log in.", "success")
        return redirect(url_for("index"))
    else:
        flash_errors(form)

    return render_template("auth/register.html", form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Render a login page."""
    form = LoginForm(request.form)

    if form.validate_on_submit():
        session.clear()
        session['user_id'] = form.user.id
        return redirect(url_for('index'))
    else:
        flash_errors(form)

    return render_template("auth/login.html", form=form)


@bp.before_app_request
def load_logged_in_user():
    """Lookup the logged in user."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    """Log out current user."""
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    """Decorator, redirects a view to the login page if no user is logged in."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
