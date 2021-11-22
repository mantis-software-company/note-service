# API/Swagger Configurations
API_TITLE = "Note Service"
API_VERSION = "v1"
OPENAPI_VERSION = "3.0.2"
OPENAPI_URL_PREFIX = "/"
OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
OPENAPI_JSON_PATH = "/v3/api-docs"
OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.0.0-rc.4/"
SWAGGER_AUTHORIZATION_SETTINGS = {
    'security': [{"bearerAuth": []}],
    'components': {
        "securitySchemes":
            {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
    }
}

# Actuator Settings
ACTUATOR_BASE_URI = "http://localhost:5000/actuator"

