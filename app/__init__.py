from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from instance.config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Register blueprint
from .routes import note_bp
app.register_blueprint(note_bp)



