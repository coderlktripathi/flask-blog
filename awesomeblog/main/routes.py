from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from awesomeblog import db
from awesomeblog.main.forms import SearchForm
from awesomeblog.models import Post

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.posted_on.desc()).paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"]
    )
    return render_template("home.html", posts=posts)


@main.route("/about")
def about():
    return render_template("about.html")


@main.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@main.route("/search")
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for("main.home"))
    page = request.args.get("page", 1, type=int)
    posts, total = Post.search(
        g.search_form.q.data, page, current_app.config["POSTS_PER_PAGE"]
    )

    if total == 0:
        flash("Oops!! no results found.", "danger")
        return redirect(url_for("main.home"))

    next_url = (
        url_for("main.search", q=g.search_form.q.data, page=page + 1)
        if total > page * current_app.config["POSTS_PER_PAGE"]
        else None
    )
    prev_url = (
        url_for("main.search", q=g.search_form.q.data, page=page - 1)
        if page > 1
        else None
    )
    return render_template(
        "search.html",
        title="Search",
        posts=posts,
        next_url=next_url,
        prev_url=prev_url,
    )
