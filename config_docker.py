# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

# Logging for Docker: log only to stdout
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
        'request_id': {
            '()': 'flask_log_request_id.RequestIDLogFilter'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['request_id'],
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'root': {
            'handlers': ['console'],
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
