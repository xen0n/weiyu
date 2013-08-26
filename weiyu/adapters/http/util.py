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
            'dummy_file_wrapper',
            'send_content_iter',
            'parse_form',
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

from ...helpers.misc import smartbytes


# This dict is pasted from Django's core/handlers/wsgi.py
# See http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
STATUS_CODES_MAP = {
        100: 'CONTINUE',
        101: 'SWITCHING PROTOCOLS',
        200: 'OK',
        201: 'CREATED',
        202: 'ACCEPTED',
        203: 'NON-AUTHORITATIVE INFORMATION',
        204: 'NO CONTENT',
        205: 'RESET CONTENT',
        206: 'PARTIAL CONTENT',
        300: 'MULTIPLE CHOICES',
        301: 'MOVED PERMANENTLY',
        302: 'FOUND',
        303: 'SEE OTHER',
        304: 'NOT MODIFIED',
        305: 'USE PROXY',
        306: 'RESERVED',
        307: 'TEMPORARY REDIRECT',
        400: 'BAD REQUEST',
        401: 'UNAUTHORIZED',
        402: 'PAYMENT REQUIRED',
        403: 'FORBIDDEN',
        404: 'NOT FOUND',
        405: 'METHOD NOT ALLOWED',
        406: 'NOT ACCEPTABLE',
        407: 'PROXY AUTHENTICATION REQUIRED',
        408: 'REQUEST TIMEOUT',
        409: 'CONFLICT',
        410: 'GONE',
        411: 'LENGTH REQUIRED',
        412: 'PRECONDITION FAILED',
        413: 'REQUEST ENTITY TOO LARGE',
        414: 'REQUEST-URI TOO LONG',
        415: 'UNSUPPORTED MEDIA TYPE',
        416: 'REQUESTED RANGE NOT SATISFIABLE',
        417: 'EXPECTATION FAILED',
        500: 'INTERNAL SERVER ERROR',
        501: 'NOT IMPLEMENTED',
        502: 'BAD GATEWAY',
        503: 'SERVICE UNAVAILABLE',
        504: 'GATEWAY TIMEOUT',
        505: 'HTTP VERSION NOT SUPPORTED',
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
