from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from awesomeblog import bcrypt, db
from awesomeblog.models import Post, User
from awesomeblog.users.forms import (
    LoginForm,
    RegistrationForm,
    RequestResetForm,
    ResetPasswordForm,
    UpdateAccountForm,
)
from awesomeblog.users.utils import save_picture, send_reset_email

users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,
            email=form.email.data,
            about_me=form.about_me.data,
            password=hashed_password,
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Your Account has been created.!!!!!", "success")
        return redirect(url_for("users.login"))
    return render_template("register.html", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")  # variable to hold the next page url
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash(
                "Invalid credentials. Please check your username and password", "danger"
            )
    return render_template("login.html", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


"""Account Route."""


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    profile_pic = url_for("static", filename="profile-pics/" + current_user.profile_pic)

    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_pic.data:
            profile_pic = save_picture(form.profile_pic.data)
            current_user.profile_pic = profile_pic

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data

        db.session.commit()
        flash("Your account has been updated", "success")
        return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template("account.html", profile_pic=profile_pic, form=form)


@users.route("/user/<string:username>")
def get_user(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.posted_on.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template("user.html", posts=posts, user=user)


@users.route("/follow/<username>")
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("User {} not found.".format(username), "danger")
        return redirect(url_for("main.home"))
    if user == current_user:
        flash("You cannot follow yourself!", "danger")
        return redirect(url_for("users.get_user", username=username))
    current_user.follow(user)
    db.session.commit()
    flash("You are following {}!".format(username), "info")
    return redirect(url_for("users.get_user", username=username))


@users.route("/unfollow/<username>")
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("User {} not found.".format(username), "danger")
        return redirect(url_for("main.home"))
    if user == current_user:
        flash("You cannot unfollow yourself!", "danger")
        return redirect(url_for("users.get_user", username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash("You are not following {}.".format(username), "info")
    return redirect(url_for("users.get_user", username=username))


@users.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(
            "An email has been sent with instructions to reset your password.", "info"
        )
        return redirect(url_for("users.login"))
    return render_template("reset_request.html", form=form)


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("users.login"))
    return render_template("reset_token.html", form=form)
