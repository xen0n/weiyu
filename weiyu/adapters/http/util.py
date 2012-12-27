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
            ]


# This dict is pasted from Django's core/handlers/wsgi.py
# See http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
STATUS_CODES_MAP = {
        100: b'CONTINUE',
        101: b'SWITCHING PROTOCOLS',
        200: b'OK',
        201: b'CREATED',
        202: b'ACCEPTED',
        203: b'NON-AUTHORITATIVE INFORMATION',
        204: b'NO CONTENT',
        205: b'RESET CONTENT',
        206: b'PARTIAL CONTENT',
        300: b'MULTIPLE CHOICES',
        301: b'MOVED PERMANENTLY',
        302: b'FOUND',
        303: b'SEE OTHER',
        304: b'NOT MODIFIED',
        305: b'USE PROXY',
        306: b'RESERVED',
        307: b'TEMPORARY REDIRECT',
        400: b'BAD REQUEST',
        401: b'UNAUTHORIZED',
        402: b'PAYMENT REQUIRED',
        403: b'FORBIDDEN',
        404: b'NOT FOUND',
        405: b'METHOD NOT ALLOWED',
        406: b'NOT ACCEPTABLE',
        407: b'PROXY AUTHENTICATION REQUIRED',
        408: b'REQUEST TIMEOUT',
        409: b'CONFLICT',
        410: b'GONE',
        411: b'LENGTH REQUIRED',
        412: b'PRECONDITION FAILED',
        413: b'REQUEST ENTITY TOO LARGE',
        414: b'REQUEST-URI TOO LONG',
        415: b'UNSUPPORTED MEDIA TYPE',
        416: b'REQUESTED RANGE NOT SATISFIABLE',
        417: b'EXPECTATION FAILED',
        500: b'INTERNAL SERVER ERROR',
        501: b'NOT IMPLEMENTED',
        502: b'BAD GATEWAY',
        503: b'SERVICE UNAVAILABLE',
        504: b'GATEWAY TIMEOUT',
        505: b'HTTP VERSION NOT SUPPORTED',
        }


def status_to_str(status):
    '''Converts status code to its description.

    '''

    return STATUS_CODES_MAP[status]


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
