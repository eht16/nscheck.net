# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

import ipaddress

from flask_wtf import FlaskForm
from wtforms.fields import StringField
from wtforms.validators import DataRequired, ValidationError
import dns.exception
import dns.name


class DomainName:
    """
    Domain name validator.
    """

    # ----------------------------------------------------------------------
    def __init__(self, message=None):
        self.message = message

    # ----------------------------------------------------------------------
    def __call__(self, form, field):
        value = field.data
        valid = False
        if value:
            try:
                dns.name.from_unicode(value)
                valid = True
            except dns.exception.DNSException:
                valid = False

        if not valid:
            message = self.message
            if message is None:
                message = field.gettext('Invalid domain name.')
            raise ValidationError(message)


class GlueRecordsForm(FlaskForm):

    domain_name = StringField(
        'Domain name',
        validators=[
            DataRequired(),
            DomainName()])


class Py3IPAddress:
    """
    IPAddress validator from wtforms 3.x using the `ip_address` module.
    """

    # ----------------------------------------------------------------------
    def __init__(self, ipv4=True, ipv6=False, message=None):
        if not ipv4 and not ipv6:
            raise ValueError(
                "IP Address Validator must have at least one of ipv4 or ipv6 enabled."
            )
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.message = message

    # ----------------------------------------------------------------------
    def __call__(self, form, field):
        value = field.data
        valid = False
        if value:
            valid = (self.ipv4 and self.check_ipv4(value)) or (
                self.ipv6 and self.check_ipv6(value)
            )

        if not valid:
            message = self.message
            if message is None:
                message = field.gettext("Invalid IP address.")
            raise ValidationError(message)

    # ----------------------------------------------------------------------
    @classmethod
    def check_ipv4(cls, value):
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return False

        if not isinstance(address, ipaddress.IPv4Address):
            return False

        return True

    # ----------------------------------------------------------------------
    @classmethod
    def check_ipv6(cls, value):
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return False

        if not isinstance(address, ipaddress.IPv6Address):
            return False

        return True


class ReverseDnsForm(FlaskForm):

    ip_address = StringField(
        'IP address',
        validators=[
            DataRequired(),
            Py3IPAddress(ipv4=True, ipv6=True)])
