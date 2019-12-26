from datetime import datetime

from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from awesomeblog import db
from awesomeblog.messages.forms import MessageForm
from awesomeblog.models import Message, Notification, Post, User

msgs = Blueprint("msgs", __name__)


@msgs.route("/send_message/<recipient>", methods=["GET", "POST"])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        user.add_notification("unread_message_count", user.new_messages())
        db.session.add(msg)
        db.session.commit()
        flash("Your message has been sent.", "success")
        return redirect(url_for("users.get_user", username=recipient))
    return render_template(
        "send_message.html", title="Send Message", form=form, recipient=recipient
    )


@msgs.route("/messages")
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification("unread_message_count", 0)
    db.session.commit()
    page = request.args.get("page", 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()
    ).paginate(page, 5, False)

    return render_template("messages.html", messages=messages)


@msgs.route("/message/<int:message_id>/delete", methods=["POST"])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message.author != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash("Your message has been deleted!!", "success")
    return redirect(url_for("msgs.messages"))


@msgs.route("/notifications")
@login_required
def notifications():
    since = request.args.get("since", 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since
    ).order_by(Notification.timestamp.asc())
    return jsonify(
        [
            {"name": n.name, "data": n.get_data(), "timestamp": n.timestamp}
            for n in notifications
        ]
    )
