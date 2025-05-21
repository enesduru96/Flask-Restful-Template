from flask import Blueprint, render_template, request, redirect, make_response, flash
from flask_jwt_extended import jwt_required, create_access_token, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request, get_jwt_identity
from app.models import User, db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect

auth_bp = Blueprint("auth", __name__)

csrf = CSRFProtect()

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if User.query.filter_by(username=username).first():
            flash("User already exists", "danger")
            return redirect("/register")

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect("/login")

    return render_template("register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Invalid credentials", "danger")
            return redirect("/login")

        access_token = create_access_token(identity=username)
        resp = make_response(redirect("/home"))
        set_access_cookies(resp, access_token)
        return resp

    return render_template("login.html", form=form)

@auth_bp.route("/logout", methods=["GET"])
@csrf.exempt
def logout():
    resp = make_response(redirect("/login"))
    unset_jwt_cookies(resp)
    flash("Successfully logged out.")
    return resp


@auth_bp.route("/profile")
@jwt_required()
def profile():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    return render_template("profile.html", username=username, user=user)

@auth_bp.route("/edit-profile", methods=["GET", "POST"])
@jwt_required()
def edit_profile():
    form = EditProfileForm()
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    if form.validate_on_submit():
        new_username = form.username.data

        if new_username != user.username and User.query.filter_by(username=new_username).first():
            flash("Username already taken.", "danger")
            return redirect("/edit-profile")

        user.username = new_username
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect("/profile")

    form.username.data = user.username
    return render_template("edit_profile.html", form=form, username=username, user=user)


@auth_bp.route("/")
def index():
    verify_jwt_in_request(optional=True)
    identity = get_jwt_identity()

    if identity:
        return redirect("/home")
    return redirect("/login")