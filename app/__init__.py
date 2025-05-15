from flask import Flask
from flask_session import Session
from app.config import Config
from app.extensions import init_extensions
from app.auth.routes import auth_bp
from app.ai.routes import ai_bp
from app.donations.routes import donation_bp
from app.main.routes import main_bp
from app.calendar.routes import event_bp
from app.health.routes import health_bp
from app.partners.routes import partners_bp
from app.analytics.routes import analytics_bp
from app.rag.routes import health_rag
from app.files.routes import file_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    Session(app)
    CORS(app, resources={r"/*": {"origins": "*"}})
    init_extensions(app)
    register_blueprints(app)
    return app

def register_blueprints(app):
    app.register_blueprint(health_rag)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(partners_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(donation_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(event_bp)

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
