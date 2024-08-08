from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from instance.config import Config
from flask_restx import Api
from flask_cors import CORS


# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
api = Api(app, version="1.0", title="Notes API", description="A simple Notes API")
# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['SECRET_KEY']='thisissecretkey'

# Register blueprint
from .routes import note_bp
from .routes.user_routes import user_bp
from .routes.category_routes import category_bp

app.register_blueprint(note_bp)
app.register_blueprint(user_bp)
app.register_blueprint(category_bp)
