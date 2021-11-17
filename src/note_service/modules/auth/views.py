import json

import requests
from flask import Blueprint, current_app, request, redirect, make_response
from oauthlib.oauth2 import WebApplicationClient

auth_blueprint = Blueprint('auth', 'auth', url_prefix='/auth')


@auth_blueprint.route("/login")
def login():
    sso_provider_cfg = requests.get(current_app.config.get("SSO_DISCOVERY_URL")).json()
    authorization_endpoint = sso_provider_cfg["authorization_endpoint"]
    client = WebApplicationClient(current_app.config.get("SSO_CLIENT_ID"))
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=f"{request.base_url}/callback",
        scope=["email", "profile"],
    )
    return redirect(request_uri)


@auth_blueprint.route("/login/callback")
def callback():
    code = request.args.get("code")
    sso_provider_cfg = requests.get(current_app.config.get("SSO_DISCOVERY_URL")).json()
    token_endpoint = sso_provider_cfg["token_endpoint"]
    client = WebApplicationClient(current_app.config.get("SSO_CLIENT_ID"))
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config.get("SSO_CLIENT_ID"), current_app.config.get("SSO_CLIENT_SECRET")),
    )
    token = client.parse_request_body_response(json.dumps(token_response.json()))
    access_token = token["access_token"]

    print(access_token)
    response = make_response(redirect(current_app.config.get("AUTH_FINAL_REDIRECTION_URI")))
    response.set_cookie(current_app.config.get("JWT_COOKIE_NAME"), access_token)
    return response
