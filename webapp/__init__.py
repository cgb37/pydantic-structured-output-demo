from quart import Quart, jsonify


def create_app() -> Quart:
    """Application factory for the Quart app."""
    app = Quart(__name__, template_folder="templates", static_folder="static")

    # Register blueprints
    from .home import bp as home_bp

    app.register_blueprint(home_bp)

    # Add a health endpoint only if it's not already registered. This avoids
    # duplicate endpoint registration when the reloader imports modules twice.
    if "health" not in app.view_functions:
        @app.route("/health", endpoint="health")
        async def health():
            return jsonify({"status": "ok"}), 200

    return app
