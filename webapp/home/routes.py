"""Home blueprint routes."""
from quart import Blueprint, render_template

bp = Blueprint("home", __name__)


@bp.route("/")
async def index():
    """Home page."""
    return await render_template("home/index.html")
