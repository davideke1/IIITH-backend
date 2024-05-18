from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs
import jwt
from django.conf import settings

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(public_id=payload["public_id"])
        return user
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except (jwt.InvalidTokenError, User.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        token = None
        print("WebSocket headers:", scope['headers'])
        for name, value in scope['headers']:
            if name.lower() == b'authorization':
                token = value.decode().replace('Bearer ', '')
                break
        print("Extracted token:", token)


        if token:
            try:
                scope['user'] = await get_user_from_token(token)
            except ValueError as e:
                await send({
                    "type": "websocket.close",
                    "code": 4001,  # Custom close code for token expiration
                })
                return
        else:
            scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)
