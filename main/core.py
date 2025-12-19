from .app import app

import main.routes
from main.api import api_bp

# Register API blueprint
app.register_blueprint(api_bp)