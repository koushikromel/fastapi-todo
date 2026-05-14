from fastapi import APIRouter, Request, Depends
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

from app.config import get_settings

auth_router = APIRouter()
oauth = OAuth()

settings = get_settings()

if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET.get_secret_value(),
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET:
    oauth.register(
        name='github',
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET.get_secret_value(),
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )

@auth_router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@auth_router.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        if user:
            request.session['user'] = dict(user)
    except Exception as e:
        return {"error": str(e)}
    return RedirectResponse(url="/")

@auth_router.get("/login/github")
async def login_github(request: Request):
    redirect_uri = request.url_for('auth_github')
    return await oauth.github.authorize_redirect(request, redirect_uri)

@auth_router.get("/auth/github")
async def auth_github(request: Request):
    try:
        token = await oauth.github.authorize_access_token(request)
        resp = await oauth.github.get('user', token=token)
        resp.raise_for_status()
        user = resp.json()

        # GitHub might return null for email if it's private, fetch it from the emails endpoint
        if user and not user.get('email'):
            emails_resp = await oauth.github.get('user/emails', token=token)
            emails_resp.raise_for_status()
            emails = emails_resp.json()
            primary_email = next((email['email'] for email in emails if email['primary']), None)
            user['email'] = primary_email

        if user:
            # We map GitHub user info to our expected session user info format
            request.session['user'] = {
                'name': user.get('name') or user.get('login'),
                'email': user.get('email'),
                'sub': str(user.get('id')),
            }
    except Exception as e:
        return {"error": str(e)}
    return RedirectResponse(url="/")

@auth_router.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url="/")
