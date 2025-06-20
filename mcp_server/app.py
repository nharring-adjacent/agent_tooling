from flask import Flask
from flask_apscheduler import APScheduler
import logging

# Initialize extensions
scheduler = APScheduler()

# In-memory store for requests - to be accessible by tasks if needed, or pass it around.
# This is already defined in routes.py, ideally, this should be managed by a dedicated module
# For now, tasks.py will import it from routes.py or be passed it.
# _filing_requests_store = {} # See routes.py for definition

def create_app():
    app = Flask(__name__)
    app.config["SCHEDULER_API_ENABLED"] = True # Allows management of scheduled jobs

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not app.logger.handlers: # Avoid adding multiple handlers during reloads in debug mode
        app.logger.addHandler(handler)

    app.logger.info("Flask app created and configured.")

    # Initialize scheduler
    if not scheduler.running:
        scheduler.init_app(app)
        scheduler.start()
        app.logger.info("APScheduler initialized and started.")
    else:
        app.logger.info("APScheduler already running.")


    # Register blueprints
    from mcp_server.api import routes as api_routes
    app.register_blueprint(api_routes.bp)
    app.logger.info("API blueprint registered.")

    @app.route('/')
    def hello():
        return "MCP Server is running!"

    return app

# The following is for running with `python mcp_server/app.py`
# For production, use a WSGI server like Gunicorn
if __name__ == '__main__':
    app = create_app()
    # Note: Flask's built-in server is not for production.
    # The reloader can cause scheduler to initialize multiple times if not handled.
    app.run(debug=True, use_reloader=False) # use_reloader=False is important for APScheduler
