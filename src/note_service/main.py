import logging
from datetime import datetime

from flask import Flask
from flask_cors import CORS
from flask_uuid import FlaskUUID
from flask_smorest import Api
from pyctuator.health.db_health_provider import DbHealthProvider
from pyctuator.pyctuator import Pyctuator

from note_service.modules.auth.views import auth_blueprint
from note_service.modules.rest.views import notes
from note_service.database import db
from note_service.utils.settings import apply_settings

app = Flask(__name__)
flask_uuid = FlaskUUID(app)
CORS(app)

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

apply_settings(app)
flask_uuid.init_app(app)
db.init_app(app)
db.create_all(app=app)
actuator = Pyctuator(
    app,
    app_name='note_service',
    app_description='Note Service API',
    app_url=f"http://{app.config['SERVER_NAME']}/",
    pyctuator_endpoint_url=app.config.get("ACTUATOR_BASE_URI"),
    registration_url=None
)
actuator.set_build_info(
    name="note_service",
    version="1.0.0",
    time=datetime.fromisoformat("2021-10-12T00:00"),
)
db_engine = db.get_engine(app)
actuator.register_health_provider(DbHealthProvider(db_engine))
api = Api(app, spec_kwargs=app.config.get("SWAGGER_AUTHORIZATION_SETTINGS"))
Api.DEFAULT_ERROR_RESPONSE_NAME = None
api.register_blueprint(notes)
app.register_blueprint(auth_blueprint)


if __name__ == "__main__":
    app.run()
