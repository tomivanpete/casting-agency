from auth import AUTH0_DOMAIN, API_AUDIENCE, CLIENT_ID


def get_auth0_login_url(redirect_uri):
    """Builds the Auth0 login page URL."""
    return 'https://' + AUTH0_DOMAIN + '/authorize?audience=' + \
        API_AUDIENCE + '&response_type=token&client_id=' + \
        CLIENT_ID + '&redirect_uri=' + redirect_uri


class Config(object):
    """Default app config."""
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = False


class ProductionConfig(Config):
    """App config for Production environment."""
    DEBUG = False
    AUTH0_LOGIN = get_auth0_login_url(
        'https://tomivanpete-casting-agency.herokuapp.com/api/healthcheck')


class DevelopmentConfig(Config):
    """App config for Development environment."""
    DEVELOPMENT = True
    DEBUG = True
    AUTH0_LOGIN = get_auth0_login_url('http://localhost:5000/api/healthcheck')
