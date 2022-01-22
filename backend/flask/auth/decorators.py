from backend.services import AuthTokenService
from flask import request
import functools

def token_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwarg):
        token = request.cookies.get('AuthToken')

        if not token:
            return "Invalid token", 400

        if not AuthTokenService.check_token(token):
            return "Invalid token", 400

        response = func(*args, **kwarg)
        return response

    return wrapper
