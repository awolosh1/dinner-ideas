import json
import os
from fastapi import FastAPI
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError


CONF_URL = "https://github.com/login/oauth/.well-known/openid-configuration"
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config, undefined
from typing import Any, Callable, Mapping, TypeVar
import logging

oauth = OAuth()
oauth.register(
    name="github",
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)
