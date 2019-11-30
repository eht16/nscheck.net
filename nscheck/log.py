# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

import logging

from flask import current_app


# Supporting helpers for logging.
# Stolen from Django.


class RequireDebugTrue(logging.Filter):

    # ----------------------------------------------------------------------
    def filter(self, record):
        if current_app:
            return current_app.debug

        # if no app is available, assume DEBUG mode is active
        return True
