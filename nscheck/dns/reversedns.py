# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

import dns.resolver
import dns.reversename

from .base import DnsBase


class ReverseDnsResolver(DnsBase):

    # ----------------------------------------------------------------------
    def query_ptr(self, ip_address):
        ip_address_reversed = self._reverse_ip_address(ip_address)
        try:
            answer = self._resolve(ip_address_reversed, 'PTR')
        except dns.resolver.NXDOMAIN:
            message = 'No PTR found for {}'.format(ip_address)
            return [message]
        return answer

    # ----------------------------------------------------------------------
    def _reverse_ip_address(self, ip_address):
        return str(dns.reversename.from_address(ip_address))

    # ----------------------------------------------------------------------
    def query_nameserver_for_ptr_zone(self, ip_address, ip_address_reversed=None):
        try:
            if ip_address_reversed is None:
                ip_address_reversed = self._reverse_ip_address(ip_address)

            answer = self._resolve(ip_address_reversed, 'NS')
            return self._factor_nameserver_list(answer)
        except (dns.resolver.NoNameservers, dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            # skip the last octet and try again (recursively)
            new_ip_address_reversed = self._factor_next_reversed_ip_name(ip_address_reversed)
            if new_ip_address_reversed:
                return self.query_nameserver_for_ptr_zone(ip_address, new_ip_address_reversed)

            return None

    # ----------------------------------------------------------------------
    def _factor_next_reversed_ip_name(self, ip_address_reversed):
        parts = ip_address_reversed.split('.')
        if len(parts) > 2:
            # IPv6: skip the last 4 dots
            if ip_address_reversed.endswith('ip6.arpa.'):
                skip = 4
            else:
                skip = 1

            new_ip_address_reversed = '.'.join(parts[skip:])
            return new_ip_address_reversed

        return None
