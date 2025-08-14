from quart import Quart, jsonify, request
import logging
import os
from .config import get_config


def create_app() -> Quart:
    """Application factory for the Quart app."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")
    app = Quart(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Load configuration
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Configure logging
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    logging.basicConfig(level=log_level)
    
    # Error handlers
    @app.errorhandler(404)
    async def not_found(error):
        """Handle 404 errors."""
        if request.is_json:
            return jsonify({"error": "Resource not found"}), 404
        return jsonify({"error": "Page not found"}), 404
    
    @app.errorhandler(500)
    async def internal_error(error):
        """Handle 500 errors."""
        app.logger.error(f"Internal error: {error}")
        return jsonify({"error": "Internal server error"}), 500
    
    @app.errorhandler(400)
    async def bad_request(error):
        """Handle 400 errors."""
        return jsonify({"error": "Bad request"}), 400

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
