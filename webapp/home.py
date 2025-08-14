from quart import Blueprint, render_template

bp = Blueprint("home", __name__)


@bp.route("/")
async def index():
    return await render_template("home/index.html")
