#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / adapter / http / CORS implementation
#
# Copyright (C) 2014 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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
        'CORSReflexHelper',
        ]

import re
import six

from ...helpers.misc import smartstr
from ...helpers.annotation import get_annotation
from ...reflex.classes import ReflexResponse

HTTP_TOKEN_RE = re.compile(r"[!#$%&'*+.0-9A-Z^_`a-z|~-]+")


def is_token(s):
    return HTTP_TOKEN_RE.match(s) is not None


class CORSReflexHelper(object):
    def __init__(self, config):
        # enable CORS by default
        # XXX Is this a security concern? As weiyu is mainly focused at
        # providing API service these days, it's really hard to not make CORS
        # the default behavior...
        enabled = self.enabled = config.get('enabled', True)

        if enabled:
            # List of origins
            origins = config.get('origins', None)
            self.allow_all = origins is None
            if self.allow_all:
                self.list_origins = set()
            else:
                if isinstance(origins, six.text_type):
                    self.list_origins = {origins, }
                else:
                    self.list_origins = set(origins)

            # "Supports credentials" flag
            self.credentials = config.get('credentials', True)

            # Access-Control-Max-Age
            self.max_age = config.get('max_age', 0)

            # Default exposed headers
            exposed_headers = config.get('exposed_headers', [])
            exposed_headers = list(set(i.lower() for i in exposed_headers))
            self.exposed_headers = exposed_headers

    def handle_cors(self, request):
        # ensure the attribute's presence
        request.cors_preflight = False

        if not self.enabled:
            return False, None

        origin = request.origin
        if origin is None:
            return False, None

        # check origin case-sensitively
        if not self.allow_all and origin not in self.list_origins:
            return False, None

        # preflight?
        preflight = request.cors_preflight = request.method == 'OPTIONS'
        if preflight:
            return self.cors_preflight(request)

        # FIXME: proper "simple request" detection as mandated by standard!
        return self.cors_simple(request)

    def cors_simple(self, request):
        return True, None

    def cors_preflight(self, request):
        # Access-Control-Request-Method
        method = request.cors_request['method']
        if method is None:
            return False, None

        method = smartstr(method)
        if not is_token(method):
            return False, None

        # Access-Control-Request-Headers
        headers_value = request.cors_request['headers']
        if headers_value is None:
            header_field_names = []
        else:
            headers_value = smartstr(headers_value)
            header_field_names = [i.strip() for i in headers_value.split(',')]
            if not all(is_token(i) for i in header_field_names):
                return False, None

        # check list of methods
        view_fn = request.callback_info[0]
        try:
            allowed_methods = get_annotation(view_fn, 'allowed_methods')
        except KeyError:
            # no @only_methods used, accept all methods
            allowed_methods = None

        # check if requested method is allowed
        if allowed_methods is not None and method not in allowed_methods:
            # method not allowed, return failure
            return False, None

        # TODO: check *list of headers*

        # set preflight response headers
        # Access-Control-Allow-Methods
        headers = [
                ('Access-Control-Allow-Methods', method, ),
                ]

        # Access-Control-Allow-Headers
        allow_headers_val = ', '.join(header_field_names)
        headers.append(
                ('Access-Control-Allow-Headers', allow_headers_val, ),
                )

        # Access-Control-Max-Age
        if self.max_age > 0:
            headers.append(
                    ('Access-Control-Max-Age', str(self.max_age), ),
                    )

        return True, ReflexResponse(204, {}, {'headers': headers, }, request)

    def cors_postprocess(self, response):
        request = response.request
        if not request.is_cors:
            return

        # Access-Control-Allow-Origin
        cors_headers = [
                ('Access-Control-Allow-Origin', request.origin, ),
                ]

        # Access-Control-Allow-Credentials
        if self.credentials:
            cors_headers.append(
                    ('Access-Control-Allow-Credentials', 'true', ),
                    )

        # Access-Control-Expose-Headers
        if self.exposed_headers:
            exposed_headers_val = ', '.join(self.exposed_headers)
            cors_headers.append(
                    ('Access-Control-Expose-Headers', exposed_headers_val, ),
                    )

        try:
            response.http_headers
        except AttributeError:
            response.http_headers = []

        response.http_headers.extend(cors_headers)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
