import os
from secrets import token_hex
from PIL import Image

from blog import app, bcrypt, db
from blog.forms import LoginForm, RegistrationForm, UpdateAccountForm
from blog.models import Post, User
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

posts = [
    {
        "author": "John Smith",
        "title": "Blog Post 1",
        "content": "First post content",
        "date_posted": "April 20, 2019",
    },
    {
        "author": "Wonder Women",
        "title": "Blog Post 2",
        "content": "Second post content",
        "date_posted": "April 21, 2019",
    },
]


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your Account has benn created.!!!!!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next') # variable to hold the next page url
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please check your username and password", "danger")
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(picture):
    random_hex = token_hex(8)
    _, file_extension = os.path.splitext(picture.filename)
    picture_name = random_hex + file_extension
    picture_path = os.path.join(app.root_path, 'static/profile-pics', picture_name)
    output_size = (200, 200)
    i = Image.open(picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_name

"""Account Route."""
@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    profile_pic = url_for('static', filename='profile-pics/' + current_user.profile_pic)

    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_pic.data:
            profile_pic = save_picture(form.profile_pic.data)
            current_user.profile_pic = profile_pic

        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', profile_pic=profile_pic, form=form)
