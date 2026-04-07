import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import create_app
from src.logger import logger

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 3001))
    logger.info(f"Server listening on port {port}")
    app.run(host='0.0.0.0', port=port, debug=os.getenv('NODE_ENV') != 'production')
