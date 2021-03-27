import json
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-tx59k7ac.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'castingagency'
CLIENT_ID = 'pu4pYwaoNzPFl524FBZbkkNattcO6rN9'


class AuthError(Exception):
    """A standardized way to communicate auth failure modes.

    Attributes:
        error: Error message describing the failure.
        status_code: HTTP status code representing the failure.
    """

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Attempts to get the bearer token from the request headers.

    Raises:
        AuthError: If no Authorization header is found, or if the
        request header is malformed.
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def verify_decode_jwt(token):
    """Decodes a JWT from Auth0.

    Args:
        token: A JSON web token string.

    Returns:
        The decoded JWT payload.

    Raises:
        AuthError: If the JWT is malformed, expired, or not valid for
        the given Auth0 domain/application.

    !!NOTE urlopen has a common certificate error described here:
    https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
    """
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, \
                    check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 401)
    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 401)


def check_permissions(permission, payload):
    """Verifies permissions in a JWT payload.

    Args:
        permission: The string permission to verify.
        payload: A decoded JWT payload.

    Returns:
        True if the given permission is in the JWT payload.

    Raises:
        AuthError: If the payload does not contain any permissions, or if
                   the given permission is not included in the payload.
    """
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT'
        }, 403)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found'
        }, 403)
    return True


def requires_auth(permission='', test_config=False):
    """Decorator method that checks for the given permission in the request.

    Args:
        permission: The permission to validate.
        test_config: Boolean flag used to bypass authorization
                     checks during unit tests.

    Raises:
        AuthError: If the permission is not found,
                   or parsing the Authorization header fails.
    """
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            payload = ''
            if not test_config:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
