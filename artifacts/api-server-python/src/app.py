import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import logger

def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Dirs for static assets
    frontend_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "sales-ai"
    ))
    public_dir = os.path.join(frontend_dir, "public")

    @app.route('/')
    def serve_index():
        """Serve the main index.html"""
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/logo.png')
    def serve_logo():
        """Serve logo"""
        return send_from_directory(public_dir, 'logo.png')

    @app.route('/sample.csv')
    def serve_csv():
        """Serve sample.csv file"""
        try:
            return send_from_directory(public_dir, 'sample.csv')
        except Exception as e:
            logger.error(f"Error serving sample.csv: {e}")
            return {"error": "File not found"}, 404
    
    # Register routes
    from src.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.errorhandler(404)
    def not_found(error):
        # Fall back to index.html for SPA routing
        return send_from_directory(frontend_dir, 'index.html')
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {"error": "Internal server error"}, 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 3001))
    logger.info(f"Server listening on port {port}")
    app.run(host='0.0.0.0', port=port, debug=os.getenv('NODE_ENV') != 'production')
