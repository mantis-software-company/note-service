import traceback
from functools import wraps
from http import HTTPStatus

import jwt
import requests
from flask import request, current_app
from flask_smorest import abort
from jwt import PyJWKClient


def _parse_jwt_user(token):
    authorized_group = current_app.config.get("AUTHORIZED_GROUP")

    try:
        sso_provider_cfg = requests.get(current_app.config.get("SSO_DISCOVERY_URL")).json()
    except Exception as e:
        tb = traceback.format_exc()
        abort(HTTPStatus.BAD_GATEWAY, message="Couldn't access to SSO server.", messages=tb, exc=e)

    jwks_url = sso_provider_cfg["jwks_uri"]
    jwks_client = PyJWKClient(jwks_url)
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    decoded_jwt = jwt.decode(token, signing_key.key, algorithms=["RS256"], audience="account",
                             options={"verify_exp": True})
    
    
    username = decoded_jwt.get("preferred_username")
    return username


def token_required(self):
    @wraps(self)
    def decorated(*args, **kwargs):

        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace("Bearer ", "")

        if not token:
            abort(HTTPStatus.UNAUTHORIZED, message="A valid token is missing.")

        try:
            username = _parse_jwt_user(token)
        except Exception:
            abort(HTTPStatus.UNAUTHORIZED, messsage="Token is invalid.")

        if not username:
            abort(HTTPStatus.FORBIDDEN, message="You have not sufficient permissions to access this API")

        return self(username=username, *args, **kwargs)

    return decorated
