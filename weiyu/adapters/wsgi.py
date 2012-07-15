#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / adapter / WSGI interface
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
            'WeiyuWSGIAdapter',
            ]

from ..reflex.classes import BaseReflex, ReflexRequest, ReflexResponse
from ..router import router_hub

from ..registry.provider import request as reg_request

HEADER_ENC = 'utf-8'

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


class WSGIRequest(ReflexRequest):
    def __init__(self, env, start_response, site_conf):
        super(WSGIRequest, self).__init__(env)

        self.start_response = start_response
        self.site = site_conf


class WSGIReflex(BaseReflex):
    def __init__(self):
        self.SITE_CONF = reg_request('site')
        # no more repeated lookups for handler
        # NOTE: Remember this can lead to stale value when handler got
        # dynamically updated. This is (admittedly) a VERY rare and
        # dangerous case that's simply NOT going to work, but the expected
        # behavior is documented here anyway.
        self._do_routing = router_hub.get_handler('wsgi')

    def _do_accept_request(self, env, start_response):
        return WSGIRequest(env, start_response, self.SITE_CONF)

    def _do_translate_request(self, request):
        # populate some useful fields using WSGI env
        env = request.env
        request.path = env['PATH_INFO']

        # Move routing (much) earlier so we don't waste time in processing
        # requests impossible to fulfill.
        # Note that we don't pass in "request" at this moment. The object
        # can be replaced by potential hooks, and we certainly don't want
        # a reference to be frozen in the request.
        # Return value is of format (fn, args, kwargs, route_data, )
        route_result = self._do_routing(request.path)
        request.callback_info = route_result[:-1]
        request.route_data = route_result[-1]

        # Rest of request object preparation goes here...
        request.remote_addr = env['REMOTE_ADDR']
        method = request.method = env['REQUEST_METHOD']
        length, _env_length = None, None
        try:
            _env_length = env['CONTENT_LENGTH']
        except KeyError:
            pass

        if _env_length is not None and len(_env_length) > 0:
            try:
                length = int(_env_length)
            except ValueError:
                pass
        request.content_length = length

        # read the request body if content length is given
        if length is not None and request.method == 'POST':
            request.content = env['wsgi.input'].read(length)
        else:
            request.content = None

        # TODO: add more ubiquitous HTTP request headers
        return request

    def _do_generate_response(self, request):
        fn, args, kwargs = request.callback_info
        return fn(request, *args, **kwargs)

    def _do_postprocess(self, response):
        ctx, hdrs = response.context, []

        enc = ctx.get('enc', 'utf-8')
        response.encoding = enc

        mime = ctx.get('mimetype', 'text/html')
        cont = response.content

        # encode content, if it's a Unicode string
        if issubclass(type(cont), unicode):
            response.content = cont.encode(enc, 'replace')

        # TODO: convert context into HTTP headers as much as possible
        # generate Content-Type from mimetype and charset
        contenttype = '%s; charset=%s' % (mime, enc, )
        hdrs.append(('Content-Type', contenttype, ))

        # generate Set-Cookie from cookies
        for cookie_line in ctx.get('cookies', []):
            hdrs.append(('Set-Cookie', cookie_line, ))

        response.http_headers = hdrs

        return response

    def _do_deliver_response(self, response):
        content = response.content
        status_code = response.status
        enc = response.encoding

        request = response.request
        start_response = request.start_response

        status_line = b'%d %s' % (
                status_code,
                STATUS_CODES_MAP[status_code],
                )

        # ensure all header contents are bytes
        headers = []
        for k, v in response.http_headers:
            # TODO: It's apparent that we need a smart_str helper here!!
            bytes_k = k.encode(enc) if issubclass(type(k), unicode) else k
            bytes_v = v.encode(enc) if issubclass(type(v), unicode) else v
            headers.append((bytes_k, bytes_v, ))

        start_response(status_line, headers)

        if isinstance(content, (str, unicode, )):
            yield content
        else:
            for chunk in content:
                if issubclass(type(chunk), unicode):
                    # encode and send the chunk using response.encoding
                    yield chunk.encode(enc, 'replace')
                else:
                    yield chunk


class WeiyuWSGIAdapter(object):
    def __init__(self):
        self.reflex = WSGIReflex()

    def __call__(self, env, start_response):
        return self.reflex.stimulate(env, start_response)


class WSGISession(object):
    def __init__(self, backend):
        self.backend = backend

    def pre_hook(self, request):
        self.backend.preprocess(request)

    def post_hook(self, response):
        return self.backend.postprocess(response)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
