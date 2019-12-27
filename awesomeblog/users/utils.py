import os
from secrets import token_hex

from flask import current_app, render_template
from PIL import Image

from awesomeblog.email import send_email


def save_picture(picture):
    random_hex = token_hex(8)
    _, file_extension = os.path.splitext(picture.filename)
    picture_name = random_hex + file_extension
    picture_path = os.path.join(
        current_app.root_path, 'static/profile-pics', picture_name
    )
    output_size = (200, 200)
    i = Image.open(picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_name


def send_reset_email(user):
    token = user.get_reset_token()
    subject = 'Password Reset Request'
    sender = 'noreply@awesomeblog.in'
    recipients = [user.email]
    txt_body = render_template('email/reset_password.txt', user=user, token=token)
    txt_html = render_template('email/reset_password.html', user=user, token=token)

    send_email(subject, sender, recipients, txt_body, txt_html)
