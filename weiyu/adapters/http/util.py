#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / adapter / http / utilities
#
# Copyright (C) 2012 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals, division

__all__ = [
            'status_to_str',
            'build_host_str',
            'dummy_file_wrapper',
            'send_content_iter',
            'canonicalize_http_headers',
            'gen_http_headers',
            'get_server_header',
            'HTTPHelper',
            ]

from functools import partial

try:
    import ujson as json
except ImportError:
    import json

import six

from ...helpers.misc import smartstr, smartbytes

parse_qs = six.moves.urllib.parse.parse_qs

from .cors import CORSReflexHelper

# See http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
STATUS_CODES_MAP = six.moves.http_client.responses

# Content types that can be parsed into a form
_FORM_CONTENT_HANDLERS = {}


def _form_content_handler(content_type):
    def _decorator_(fn):
        if content_type in _FORM_CONTENT_HANDLERS:
            raise ValueError(
                    "'%s' already registered as handler!" % (
                        content_type,
                        )
                    )

        _FORM_CONTENT_HANDLERS[content_type] = fn
        return fn
    return _decorator_


def status_to_str(status):
    '''Converts status code to its description.

    '''

    return STATUS_CODES_MAP[status]


def build_host_str(env):
    # Written according to the algorithm described in PEP 333.
    if 'HTTP_HOST' in env:
        return smartstr(env['HTTP_HOST'], 'utf-8', 'replace')
    else:
        server_name_str = smartstr(env['SERVER_NAME'], 'utf-8', 'replace')
        server_port = int(env['SERVER_PORT'])
        host_str_list = [server_name_str, ]

        if env['wsgi.url_scheme'] == 'https':
            if server_port != 443:
                host_str_list.append(six.text_type(server_port))
        else:
            if server_port != 80:
                host_str_list.append(six.text_type(server_port))

        return ':'.join(host_str_list)


def dummy_file_wrapper(fp, blk_sz=None):
    blk_sz = blk_sz if blk_sz is not None else 4096
    do_read = partial(fp.read, blk_sz)
    chunk = do_read()
    while len(chunk) > 0:
        yield chunk
        chunk = do_read()
    fp.close()


def send_content_iter(content, enc):
    if isinstance(content, six.string_types):
        yield smartbytes(content, enc, 'replace')
    elif isinstance(content, six.binary_type):
        yield content
    else:
        for chunk in content:
            # encode and send the chunk using response.encoding
            yield smartbytes(chunk, enc, 'replace')


@_form_content_handler('application/x-www-form-urlencoded')
def _parse_urlencoded_form(content):
    form = parse_qs(content)

    # eliminate all those 1-element lists
    for k in six.iterkeys(form):
        if len(form[k]) == 1:
            form[k] = form[k][0]

    return form


@_form_content_handler('application/json')
def _parse_json_form(content):
    return json.loads(content)


def canonicalize_http_headers(header_obj):
    if isinstance(header_obj, list):
        return header_obj
    elif isinstance(header_obj, dict):
        # most probably dict or OrderedDict, make it a plain list
        return list(six.iteritems(header_obj))
    elif isinstance(header_obj, tuple):
        return list(header_obj)

    raise ValueError(
            'unrecognized HTTP headers object: %s' % (
                repr(header_obj),
                ))


def gen_http_headers(response, __Content_Length=str('Content-Length')):
    status_code, enc = response.status, response.encoding

    status_line = str('%d %s' % (
            status_code,
            status_to_str(status_code),
            ))

    # ensure all header contents are bytes
    headers = []

    # insert a Content-Length along if response is not raw file and contains
    # a body
    if not response.is_raw_file and not response._dont_render:
        headers.append((
                __Content_Length,
                str(len(response.content)),
                ))

    for k, v in response.http_headers:
        k_bytes, v_bytes = smartbytes(k, enc), smartbytes(v, enc)
        k_str, v_str = str(k_bytes), str(v_bytes)
        headers.append((k_str, v_str, ))

    return status_line, headers


def get_server_header(__cache=[]):
    try:
        return __cache[0]
    except IndexError:
        pass

    import sys
    try:
        # PyPy
        python_ver = 'PyPy/%d.%d.%d' % sys.pypy_version_info[:3]
    except AttributeError:
        pass

    # CPython
    python_ver = 'Python/%d.%d.%d' % sys.version_info[:3]

    # weiyu
    from weiyu.__version__ import VERSION_STR
    weiyu_ver = 'weiyu/' + VERSION_STR

    header_val = ' '.join((weiyu_ver, python_ver, ))
    __cache.append((str('Server'), str(smartbytes(header_val))))
    return __cache[0]


class HTTPHelper(object):
    '''Settings-aware HTTP helper object.'''

    def __init__(self, config):
        # Request
        request_config = config.get('request', {})

        # Acceptable MIME types of POST data
        post_mime = request_config.get('post_mime', {})
        known_mimes = set(six.iterkeys(_FORM_CONTENT_HANDLERS))
        blacklisted_mimes = set(post_mime.get('blacklist', []))
        whitelisted_mimes = set(post_mime.get('whitelist', known_mimes))
        acceptable_mimes = whitelisted_mimes.difference(blacklisted_mimes)
        self._acceptable_post_mimes = frozenset(acceptable_mimes)

        # CORS
        self.cors_helper = CORSReflexHelper(config.get('cors', {}))

        # Response headers
        response_config = config.get('response', {})
        self.fixed_response_hdrs = []

        # Strict-Transport-Security
        self._init_sts(response_config.get('sts', {}))

    def parse_form(self, content_type, content):
        # canonicalize content type
        # TODO: what does a charset specified here affect? this seems
        # irrevelant for JSON or urlencoded form data...
        c_type = content_type.split(';', 1)[0]

        if c_type in self._acceptable_post_mimes:
            return _FORM_CONTENT_HANDLERS[c_type](content)

        return None

    def _init_sts(self, config):
        if not config.get('enabled', True):
            self._sts_header = None
            return

        max_age = config.get('max-age', 31536000)  # 1yr
        if not isinstance(max_age, six.integer_types):
            raise RuntimeError('STS max-age must be integer')

        include_subdomains = config.get('includeSubdomains', False)
        sts_value = 'max-age={0}'.format(max_age)
        if include_subdomains:
            sts_value += '; includeSubdomains'

        self._sts_header = ('Strict-Transport-Security', sts_value, )

    def maybe_inject_sts_headers(self, response):
        # Don't do anything if STS is disabled or if we're accessed in plain
        # HTTP. As the STS header will be ignored in plain HTTP conversations,
        # we just don't bother sending it at all.
        if self._sts_header is None or response.request.protocol != 'https':
            return

        try:
            response.http_headers
        except AttributeError:
            response.http_headers = []

        response.http_headers.append(self._sts_header)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
