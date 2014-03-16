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
            'parse_form',
            'canonicalize_http_headers',
            'gen_http_headers',
            ]

from functools import partial

try:
    # Python 3
    from urllib.parse import parse_qs
except ImportError:
    # Python 2
    from urlparse import parse_qs

try:
    import ujson as json
except ImportError:
    import json

import six

from ...helpers.misc import smartstr, smartbytes


# This dict is pasted from Django's core/handlers/wsgi.py, with letter cases
# adjusted.
# See http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
STATUS_CODES_MAP = {
        100: 'Continue',
        101: 'Switching Protocols',
        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        203: 'Non-Authoritative Information',
        204: 'No Content',
        205: 'Reset Content',
        206: 'Partial Content',
        300: 'Multiple Choices',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        304: 'Not Modified',
        305: 'Use Proxy',
        306: 'Reserved',
        307: 'Temporary Redirect',
        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Payment Required',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        407: 'Proxy Authentication Required',
        408: 'Request Timeout',
        409: 'Conflict',
        410: 'Gone',
        411: 'Length Required',
        412: 'Precondition Failed',
        413: 'Request Entity Too Large',
        414: 'Request-URI Too Long',
        415: 'Unsupported Media Type',
        416: 'Requested Range Not Satisfiable',
        417: 'Expectation Failed',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout',
        505: 'HTTP Version Not Supported',
        }

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


def parse_form(ctype, content):
    if ctype in _FORM_CONTENT_HANDLERS:
        return _FORM_CONTENT_HANDLERS[ctype](content)

    return None


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


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
