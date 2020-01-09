# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

import logging
import logging.config

from flask import Flask
from flask.logging import default_handler
from flask_bs4 import Bootstrap
from flask_log_request_id import parser, RequestID
from flask_sitemap import Sitemap
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import NotFound
from werkzeug.middleware.proxy_fix import ProxyFix

from nscheck import views
from nscheck.session import DummySessionInterface


# ----------------------------------------------------------------------
def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('../config.py')
    app.config.from_pyfile('../config_local.py', silent=True)

    # patch app to handle non root url-s behind proxy & wsgi
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Logging
    log_request_id_header_name = app.config['LOG_REQUEST_ID_HEADER_NAME']
    request_id_parser = parser.generic_http_header_parser_for(log_request_id_header_name)
    RequestID(app, request_id_parser=request_id_parser)
    logging.config.dictConfig(app.config['LOGGING'])
    logging.captureWarnings(True)  # log warnings using the logging subsystem
    app.logger.removeHandler(default_handler)  # pylint: disable=no-member

    # disable sessions
    app.session_interface = DummySessionInterface()

    # add views
    app.register_blueprint(views.blueprint_base)
    app.register_blueprint(views.blueprint_dns)
    # add "homepage" url
    app.add_url_rule('/', 'home', redirect_to='dns/reversedns')

    # error handlers
    app.register_error_handler(NotFound, views.error_handler)
    app.register_error_handler(Exception, views.error_handler)

    # add CSRF protection
    CSRFProtect(app)
    # add Bootstrap
    Bootstrap(app)
    # add sitemap
    Sitemap(app)

    return app


# ----------------------------------------------------------------------
def wsgi(*args, **kwargs):
    app = create_app()
    return app(*args, **kwargs)
