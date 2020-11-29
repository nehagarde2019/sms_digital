from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

from pyramid.security import ALL_PERMISSIONS, Allow, authenticated_userid


class RootACL(object):
    __acl__ = [
        (Allow, authenticated_userid, ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        pass


def add_role_principals(userid, request):
    return request.jwt_claims.get('user_id', userid)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('.models')
        config.include('pyramid_jinja2')
        config.include('.routes')
        config.scan()
        config.set_root_factory(RootACL)
        config.set_authorization_policy(ACLAuthorizationPolicy())
        config.include('pyramid_jwt')
        config.set_jwt_authentication_policy('5FE10366755DA0D9AF36F29CCFED26BCE2D3AA33BF7D124EBEB3E3D48A34E9D2',
                                             auth_type='Bearer',
                                             callback=add_role_principals)
    return config.make_wsgi_app()
