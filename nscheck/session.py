# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from flask.sessions import SecureCookieSessionInterface


class DummySessionInterface(SecureCookieSessionInterface):

    # ----------------------------------------------------------------------
    def open_session(self, app, request):
        """Flask-WTF supports CSRF tokens only from sessions but we do not have sessions"""
        session = super().open_session(app, request)
        csrf_field_name = app.config.get('WTF_CSRF_FIELD_NAME', 'csrf_token')
        csrf_token = request.cookies.get(csrf_field_name, None)
        if csrf_token is not None:
            session[csrf_field_name] = csrf_token

        return session

    # ----------------------------------------------------------------------
    def save_session(self, app, session, response):
        "Instead of session, just set the CSRF token as cookie"
        csrf_field_name = app.config.get('WTF_CSRF_FIELD_NAME', 'csrf_token')
        if csrf_field_name in session:
            domain = self.get_cookie_domain(app)
            path = self.get_cookie_path(app)

            httponly = self.get_cookie_httponly(app)
            secure = self.get_cookie_secure(app)
            samesite = self.get_cookie_samesite(app)
            expires = self.get_expiration_time(app, session)
            value = session[csrf_field_name]
            response.set_cookie(
                csrf_field_name,
                value,
                expires=expires,
                httponly=httponly,
                domain=domain,
                path=path,
                secure=secure,
                samesite=samesite,
            )
