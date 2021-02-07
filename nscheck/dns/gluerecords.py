# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

import logging

import dns.flags
import dns.name
import dns.query
import dns.rdatatype
import dns.resolver

from .base import DnsBase


class GlueRecordResolver(DnsBase):

    # ----------------------------------------------------------------------
    def query_glue_records(self, domain_name):
        domain_name = self._ensure_trailing_dot(domain_name)
        domain = dns.name.from_unicode(domain_name)

        # fetch parent domain nameservers
        parent_domain_nameserver_ip_addresses = self._fetch_parent_nameserver_ip_addresses(domain)
        # fetch domain's nameservers using the parent nameservers
        glue_records = self._query_glue_records(domain, parent_domain_nameserver_ip_addresses)

        return glue_records

    # ----------------------------------------------------------------------
    def _ensure_trailing_dot(self, domain_name):
        if not domain_name.endswith('.'):
            domain_name = '{}.'.format(domain_name)

        return domain_name

    # ----------------------------------------------------------------------
    def _fetch_parent_nameserver_ip_addresses(self, domain):
        parent_domain = domain.parent()
        parent_domain_nameservers = self._resolve(parent_domain, dns.rdatatype.NS)
        return self._factor_nameserver_ip_addresses(parent_domain_nameservers)

    # ----------------------------------------------------------------------
    def _factor_nameserver_ip_addresses(self, nameserver_names):
        nameservers = self._factor_nameserver_list(nameserver_names)
        nameserver_ip_addresses = list()
        for nameserver in nameservers:
            nameserver_ip_addresses.extend(nameserver.ip_addresses)

        return nameserver_ip_addresses

    # ----------------------------------------------------------------------
    def _query_glue_records(self, domain, nameservers):
        glue_records = dict()
        resolver = self._factor_resolver(nameservers)
        try:
            response = resolver.query(domain, dns.rdatatype.NS, raise_on_no_answer=False)
        except dns.resolver.NXDOMAIN as exc:
            self._log_dns_message(
                logging.INFO,
                'Error on resolving name "{}" for type "{}" using nameservers "{}": {}'.format(
                    domain.to_text(),
                    dns.rdatatype.NS,
                    ','.join(nameservers),
                    exc),
                query=domain.to_text(),
                rdtype=dns.rdatatype.NS,
                exc=exc)
            # raise the original exception
            raise

        if response.response.additional:
            for record in response.response.additional:
                if record.rdtype in (dns.rdatatype.A, dns.rdatatype.AAAA):
                    nameserver_name = record.name.to_text()
                    nameserver_ip_address = self._get_ip_address_from_record(record)
                    nameserver_ip_addresses = glue_records.setdefault(nameserver_name, list())
                    nameserver_ip_addresses.append(nameserver_ip_address)

            self._log_dns_message(
                logging.DEBUG,
                'Queried glue records for "{}" for type "{}" using nameservers "{}": {}'.format(
                    domain.to_text(),
                    dns.rdatatype.NS,
                    ','.join(nameservers),
                    ','.join([
                        glue
                        for sub_glue_records
                        in glue_records.values()
                        for glue
                        in sub_glue_records])),
                query=domain.to_text(),
                rdtype=dns.rdatatype.NS,
                answer=response.response.answer)

        return glue_records
