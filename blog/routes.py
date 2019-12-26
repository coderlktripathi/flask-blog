import os
from secrets import token_hex
from PIL import Image

from blog import app, bcrypt, db, mail
from blog.forms import (
    LoginForm,
    RegistrationForm,
    UpdateAccountForm,
    PostForm,
    RequestResetForm,
    ResetPasswordForm,
    MessageForm
)
from blog.models import Post, User, Notification, Message as MessageModal
from flask import flash, redirect, render_template, request, url_for, abort, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from datetime import datetime


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.posted_on.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data, email=form.email.data, about_me=form.about_me.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Your Account has been created.!!!!!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")  # variable to hold the next page url
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash(
                "Invalid credentials. Please check your username and password", "danger"
            )
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


def save_picture(picture):
    random_hex = token_hex(8)
    _, file_extension = os.path.splitext(picture.filename)
    picture_name = random_hex + file_extension
    picture_path = os.path.join(app.root_path, "static/profile-pics", picture_name)
    output_size = (200, 200)
    i = Image.open(picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_name


"""Account Route."""


@app.route("/account", methods=["GET", "POST"])
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
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template("account.html", profile_pic=profile_pic, form=form)


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f"Post created.!!!!!", "success")
        return redirect(url_for("home"))
    return render_template("create-post.html", form=form, legend="New Post")


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", post=post)


@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        flash("Your post has been updated!", "success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.body.data = post.body
    return render_template("create-post.html", form=form, legend="Update Post")


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!!", "success")
    return redirect(url_for("home"))


@app.route("/user/<string:username>")
def get_user(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.posted_on.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template("user.html", posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request", sender="noreply@awesomeblog.in", recipients=[user.email]
    )
    msg.body = f"""To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(
            "An email has been sent with instructions to reset your password.", "info"
        )
        return redirect(url_for("login"))
    return render_template("reset_request.html", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("login"))
    return render_template("reset_token.html", form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username), 'danger')
        return redirect(url_for('home'))
    if user == current_user:
        flash('You cannot follow yourself!', 'danger')
        return redirect(url_for('get_user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username), 'info')
    return redirect(url_for('get_user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username), 'danger')
        return redirect(url_for('home'))
    if user == current_user:
        flash('You cannot unfollow yourself!', 'danger')
        return redirect(url_for('get_user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username), 'info')
    return redirect(url_for('get_user', username=username))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = MessageModal(author=current_user, recipient=user,
                      body=form.message.data)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent.', 'success')
        return redirect(url_for('get_user', username=recipient))
    return render_template('send_message.html', title='Send Message',
                           form=form, recipient=recipient)

@app.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        MessageModal.timestamp.desc()).paginate(
            page, 5, False)

    return render_template('messages.html', messages=messages)

@app.route("/message/<int:message_id>/delete", methods=["POST"])
@login_required
def delete_message(message_id):
    message = MessageModal.query.get_or_404(message_id)
    if message.author != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash("Your message has been deleted!!", "success")
    return redirect(url_for("messages"))

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Message': Message,
            'Notification': Notification}

@app.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])