"""Flask application factory for the Sales Analysis AI backend."""

import os
import sys
from pathlib import Path

# Ensure the project root (api-server-python/) is on sys.path so that
# `from src.xxx` imports work when invoked as `python src/app.py`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from src.logger import logger

# Load .env from the api-server-python root
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    # Static asset directories
    frontend_dir = str(Path(__file__).resolve().parent.parent.parent / "sales-ai")
    public_dir = str(Path(frontend_dir) / "public")

    # ── Static file routes ───────────────────────────────────────────────
    @app.route('/')
    def serve_index():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:filename>')
    def serve_static(filename: str):
        """Serve static assets from public/, fall back to index.html for SPA."""
        try:
            return send_from_directory(public_dir, filename)
        except Exception:
            return send_from_directory(frontend_dir, 'index.html')

    # ── API blueprint ────────────────────────────────────────────────────
    from src.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # ── Error handlers ───────────────────────────────────────────────────
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {"error": "Internal server error"}, 500

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 3001))
    debug = os.getenv('APP_ENV', os.getenv('NODE_ENV', 'development')) != 'production'
    logger.info(f"Server listening on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
