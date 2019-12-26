import os
from secrets import token_hex

from flask import current_app, request, url_for
from flask_mail import Message
from PIL import Image

from awesomeblog import mail


def save_picture(picture):
    random_hex = token_hex(8)
    _, file_extension = os.path.splitext(picture.filename)
    picture_name = random_hex + file_extension
    picture_path = os.path.join(
        current_app.root_path, "static/profile-pics", picture_name
    )
    output_size = (200, 200)
    i = Image.open(picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_name


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request",
        sender="noreply@awesomeblog.in",
        recipients=[user.email],
    )
    msg.body = f"""To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)
