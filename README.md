

# Note Service
  

This project written with [Flask web framework](https://flask.palletsprojects.com/en/2.0.x/). It use [flask-smorest](https://flask-smorest.readthedocs.io/en/latest/index.html) for REST API, [Pyctuator](https://github.com/SolarEdgeTech/pyctuator) for actuator endpoint and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) for handle DB queries. Swagger UI documentation and API validations handled by flask-smorest itself. flask-smorest uses [Marshmallow](https://marshmallow.readthedocs.io/en/stable/index.html) models for marshalling and unmarshalling objects in request and response. This models also used by Swagger UI.

  
In project, different project parts divided into independent Blueprints and modules. This modules can be seen in modules directory. App modules has their own views, controllers, database models, schemas,  error handlers, decorators and utils. 

Common non-blueprint things (incl. DB instance, utils, ...) has own modules in project root.  App configs stored in [config.py](src/note_service/config.py) and can be overrided with environment variables via  `apply_settings()` function in [settings.py](src/note_service/utils/settings.py). 
  

Currently, this service has two independent blueprints: Auth (/auth) and Api (/api/v1/notes).
In Auth blueprint, there are endpoints for redirecting to SSO (/auth/login) and getting access token from SSO (/auth/login/callback).

Access token will persist in cookie for future use.
  

## Environment Variables


- `OAUTHLIB_INSECURE_TRANSPORT`: Set `True` for non-https environments

- `__SERVICE_SQLALCHEMY_DATABASE_URI`: Database URI. Ex. `sqlite:///db.sqlite`

- `__SERVICE_ACTUATOR_BASE_URI`: Full URL for actuator endpoint.

- `__SERVICE_SSO_DISCOVERY_URL`: OpenID configuration endpoint of SSO tool.

- `__SERVICE_SSO_CLIENT_ID`: SSO Client ID

- `__SERVICE_SSO_CLIENT_SECRET`: SSO Client Secret

- `__SERVICE_SSO_TARGET_AUDIENCE`: SSO Audience for JWT validation.

- `__SERVICE_JWT_COOKIE_NAME`: JWT token cookie name

- `__SERVICE_FILE_SERVICE_UPLOAD_URL`: File service api url for uploading attachment

- `__SERVICE_FILE_SERVICE_DOWNLOAD_URL`: File service api url for downloading attachment

- `__SERVICE_PDF_SERVICE_KEY_URL`: PDF service api url for securely previewing the note attachments

- `__SERVICE_AUTHORIZED_GROUP`: Set group name in SSO (Put / before it for Keycloak.)

Other application settings in [config.py](src/note_service/config.py)   could be overrided with environment variables with `__SERVICE_` prefix.

