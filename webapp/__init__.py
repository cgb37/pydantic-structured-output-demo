from quart import Quart, jsonify


def create_app() -> Quart:
    """Application factory for the Quart app."""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")
    app = Quart(__name__, template_folder=template_dir, static_folder=static_dir)

    # Register blueprints
    from .home import bp as home_bp
    from .api import bp as api_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Add a health endpoint only if it's not already registered. This avoids
    # duplicate endpoint registration when the reloader imports modules twice.
    if "health" not in app.view_functions:
        @app.route("/health", endpoint="health")
        async def health():
            return jsonify({"status": "ok"}), 200

    return app
