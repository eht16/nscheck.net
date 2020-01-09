# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from flask import Blueprint, current_app, flash, render_template
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import NotFound

from nscheck.dns.gluerecords import GlueRecordResolver
from nscheck.dns.reversedns import ReverseDnsResolver
from nscheck.forms import GlueRecordsForm, ReverseDnsForm


blueprint_base = Blueprint('base', __name__, url_prefix='/')  # pylint: disable=invalid-name
blueprint_dns = Blueprint('dns', __name__, url_prefix='/dns')  # pylint: disable=invalid-name


# ----------------------------------------------------------------------
@blueprint_base.route('/privacy')
def privacy():
    return render_template('privacy.html')


# ----------------------------------------------------------------------
@blueprint_dns.route('/gluerecords', methods=('GET', 'POST'))
def gluerecords():
    status_code = 200
    domain_name_validation_regex = \
        r'^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,8}\.?$'

    form = GlueRecordsForm()

    template_context = dict(form=form, domain_name_validation_regex=domain_name_validation_regex)
    if form.validate_on_submit():
        resolvers = current_app.config['DNS_RESOLVERS']
        domain_name = form.domain_name.data
        domain_name = domain_name.lower()
        try:
            resolver = GlueRecordResolver(resolvers, logger=current_app.logger)
            glue_records = resolver.query_glue_records(domain_name)
        except Exception as exc:
            status_code = 500
            message = 'Error on glue records resolution for "{}": {}'.format(domain_name, exc)
            flash(message, 'error')
            extra = dict(dns=dict(question=dict(name=domain_name)))
            current_app.logger.exception(message, extra=extra)
        else:
            message = 'Successfully queried glue records for "{}"'.format(domain_name)
            current_app.logger.debug(message, extra=dict(dns=dict(question=dict(name=domain_name))))
            result = dict(glue_records=glue_records)
            return render_template('dns/gluerecords.html', result=result, **template_context)

    # report validation errors
    if form.is_submitted():
        for error_message in form.domain_name.errors:
            flash('Domain name: {}'.format(error_message), 'error')
            status_code = 400

    return render_template('dns/gluerecords.html', **template_context), status_code


# ----------------------------------------------------------------------
@blueprint_dns.route('/rdns')
@blueprint_dns.route('/reversedns', methods=('GET', 'POST'))
def reversedns():
    status_code = 200

    form = ReverseDnsForm()
    if form.validate_on_submit():
        resolvers = current_app.config['DNS_RESOLVERS']
        ip_address = form.ip_address.data
        ip_address = ip_address.lower()
        try:
            resolver = ReverseDnsResolver(resolvers, logger=current_app.logger)
            ptrs = resolver.query_ptr(ip_address)
            nameservers = resolver.query_nameserver_for_ptr_zone(ip_address)
        except Exception as exc:
            status_code = 500
            message = 'Error on reverse DNS resolution for "{}": {}'.format(ip_address, exc)
            extra = dict(dns=dict(question=dict(name=ip_address)))
            flash('{}'.format(exc), 'error')
            current_app.logger.exception(message, extra=extra)
        else:
            message = 'Successfully resolved "{}" to: "{}"'.format(ip_address, ', '.join(ptrs))
            current_app.logger.debug(message, extra=dict(dns=dict(question=dict(name=ip_address))))
            reverse_dns = dict(ptrs=ptrs, nameservers=nameservers)
            return render_template('dns/reversedns.html', form=form, reverse_dns=reverse_dns)

    # report validation errors
    if form.is_submitted():
        for error_message in form.ip_address.errors:
            flash('IP address: {}'.format(error_message), 'error')
            status_code = 400

    return render_template('dns/reversedns.html', form=form), status_code


# ----------------------------------------------------------------------
@blueprint_base.after_request
@blueprint_dns.after_request
def set_response_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


# ----------------------------------------------------------------------
def error_handler(exc):
    # raise all exceptions in debug mode
    if current_app.debug:
        raise exc
    # log
    current_app.logger.exception('An error occurred: {}'.format(exc))
    # response
    if isinstance(exc, NotFound):
        return render_template('error_404.html', e=exc), 404
    if isinstance(exc, CSRFError):
        return render_template('error_csrf.html', e=exc), 400

    return render_template('error_500.html', e=exc), 500
