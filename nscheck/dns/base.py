# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from collections import namedtuple
import logging

import dns.opcode
import dns.rcode
import dns.rdatatype
import dns.resolver
import dns.reversename


DNS_IP_RDTYPES = (dns.rdatatype.A, dns.rdatatype.AAAA)
NameServer = namedtuple('NameServer', ('nameserver', 'ip_addresses'))


########################################################################
class DnsBase:

    # ----------------------------------------------------------------------
    def __init__(self, nameservers, logger):
        self._nameservers = nameservers
        self._logger = logger

    # ----------------------------------------------------------------------
    def _resolve(self, fqdn, rdtype, nameservers=None, ignore_errors=False):
        try:
            resolver = self._factor_resolver(nameservers)
            answer = resolver.query(fqdn, rdtype)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer) as exc:
            self._log_dns_message(
                logging.INFO,
                'Error on resolving name "{}" for type "{}": {}'.format(fqdn, rdtype, exc),
                query=fqdn,
                rdtype=rdtype,
                exc=exc)
            if ignore_errors:
                return list()
            # raise the original exception
            raise
        else:
            result = [rr.to_text() for rr in answer]
            self._log_dns_message(
                logging.DEBUG,
                'Resolved name "{}" for type "{}" to: {}'.format(fqdn, rdtype, ', '.join(result)),
                query=fqdn,
                rdtype=rdtype,
                answer=answer)
            return result

    # ----------------------------------------------------------------------
    def _factor_resolver(self, nameservers=None):
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = nameservers or self._nameservers
        self._logger.debug('Using nameservers "{}"'.format(','.join(resolver.nameservers)))
        return resolver

    # ----------------------------------------------------------------------
    def _log_dns_message(self, level, message, query, rdtype=None, answer=None, exc=None):
        """Add Elastic ECS fields"""
        response = None
        extra = dict()
        extra['dns'] = dict()
        extra['dns']['type'] = 'answer' if not answer and not exc else 'query'
        extra['dns']['question'] = dict()
        extra['dns']['question']['class'] = 'IN'
        extra['dns']['question']['name'] = query
        if rdtype:
            extra['dns']['question']['type'] = rdtype
        if exc:
            response = exc.kwargs.get('response')
        if answer:
            response = answer.response

        if response:
            extra['dns']['id'] = response.id
            extra['dns']['opcode'] = dns.opcode.to_text(response.opcode())
            extra['dns']['response_code'] = dns.rcode.to_text(response.rcode())
            resolved_ips = list()
            answers = list()
            for record in response.answer:
                ecs_rr = dict()
                ecs_rr['class'] = 'IN'
                ecs_rr['type'] = dns.rdatatype.to_text(record.rdtype)
                ecs_rr['data'] = self._get_ip_address_from_record(record)
                ecs_rr['ttl'] = record.ttl
                answers.append(ecs_rr)
                if record.rdtype in DNS_IP_RDTYPES:
                    resolved_ips.append(ecs_rr['data'])

            if resolved_ips:
                extra['dns']['resolved_ip'] = resolved_ips
            if answers:
                extra['dns']['answers'] = answers

        if isinstance(exc, (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN)):
            exc = None  # do not log traceback for common, expected errors

        self._logger.log(level, message, extra=extra, exc_info=exc)

    # ----------------------------------------------------------------------
    def _get_ip_address_from_record(self, record):
        if record.items and len(record.items) == 1:
            item_keys = list(record.items.keys())
            item_key = item_keys[0]
            return item_key.to_text()

    # ----------------------------------------------------------------------
    def _factor_nameserver_list(self, nameserver_names):
        nameservers = list()
        for nameserver_name in nameserver_names:
            nameserver_ipv4_addresses = self._resolve(nameserver_name, 'A', ignore_errors=True)
            nameserver_ipv6_addresses = self._resolve(nameserver_name, 'AAAA', ignore_errors=True)
            ip_addresses = nameserver_ipv4_addresses + nameserver_ipv6_addresses
            nameserver = NameServer(nameserver_name, ip_addresses)
            nameservers.append(nameserver)
        return nameservers
