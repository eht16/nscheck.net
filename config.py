# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

SECRET_KEY = 'change-me'
PREFERRED_URL_SCHEME = 'https'

SITEMAP_URL_SCHEME = 'https'
SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS = True

BOOTSTRAP_SERVE_LOCAL = True

DNS_RESOLVERS = [
    # OpenNIC
    '194.36.144.87',
    '2a03:4000:4d:c92:88c0:96ff:fec6:b9d',
    '94.247.43.254',
    '2a00:f826:8:1::254',
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
                '%(asctime)s %(name)s %(process)d %(threadName)s '
                '%(levelname)s [%(request_id)s] %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'nscheck.log.RequireDebugTrue'
        },
        'request_id': {
            '()': 'flask_log_request_id.RequestIDLogFilter'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true', 'request_id'],
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'nscheck.log',
            'filters': ['request_id'],
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': [],
            'propagate': True,
            'level': 'DEBUG',
        },
        'werkzeug': {
            'handlers': [],
            'propagate': False,
            'level': 'DEBUG',
        },
    }
}

LOG_REQUEST_ID_LOG_ALL_REQUESTS = False
LOG_REQUEST_ID_HEADER_NAME = 'X-Http-Request-Id'

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Lax'
