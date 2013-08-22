#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / adapter / http / base class
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
            'BaseHTTPReflex',
            ]

from ...helpers.misc import smartbytes

from ...registry.provider import request as reg_request

from ...reflex.classes import BaseReflex
from ...router import router_hub
from ...session import session_hub
from ...signals import signal_hub
from ...rendering import render_hub

from .. import adapter_hub

# Status codes that cannot have response body
# Used to prevent rendering code from being invoked
# TODO: add more of them
NO_RESP_BODY_STATUSES = {405, }


@adapter_hub.declare_middleware('session')
class HTTPSessionMiddleware(object):
    def __init__(self):
        # get options
        site = reg_request('site')

        # assume session config is present if this middleware is used
        ses_conf = site['session']
        ses_backend, ses_opts = ses_conf['backend'], ses_conf['options']

        # request a session backend
        self._backend = session_hub.do_handling(ses_backend, ses_opts)

    def do_pre(self, request):
        self._backend.preprocess(request)

    def do_post(self, response):
        self._backend.postprocess(response)


class BaseHTTPReflex(BaseReflex):
    def __init__(self):
        self.SITE_CONF = reg_request('site')
        # no more repeated lookups for handler
        # NOTE: Remember this can lead to stale value when handler got
        # dynamically updated. This is (admittedly) a VERY rare and
        # dangerous case that's simply NOT going to work, but the expected
        # behavior is documented here anyway.
        self._do_routing = router_hub.get_handler('http')

    def _do_translate_request(self, request):
        # Middleware
        # TODO: ability to skip response generation?
        signal_hub.fire_nullok('http-middleware-pre', request)

        return request

    def _do_generate_response(self, request):
        fn, args, kwargs = request.callback_info
        response = fn(request, *args, **kwargs)

        # Middleware
        signal_hub.fire_nullok('http-middleware-post', response)

        return response

    def _do_postprocess(self, response):
        # Render the response early
        # TODO: find a way to extract all the literals out
        request = response.request
        ctx, hdrs, extras = response.context, [], {}
        render_in = cont = mime = None
        dont_render = False

        # are we hijacked by some other library (e.g. socketio)?
        if ctx.get('request_vanished', False):
            # All further actions starting from accepting request are
            # performed by the other library, so we can't do anything
            # in this case. Just bail out.
            response._vanished = True
            return response

        response._vanished = False

        # encoding
        enc = response.encoding = ctx.get('enc', 'utf-8')

        # is this a raw file push request?
        response.is_raw_file = ctx.get('is_raw_file', False)
        if response.is_raw_file and 'sendfile_fp' in response.content:
            # request to send raw file valid, suppress rendering
            dont_render = True
            response.raw_fp = response.content['sendfile_fp']
            response.raw_blksz = response.content.get('blocksize', None)

            # If rendering needs to be suppressed and content is not a raw
            # file, we cannot safely assume the data stream is of type
            # text/html then...
            mime = ctx.get('mimetype', 'application/octet-stream')

        # is this an error response which cannot have response body?
        # TODO: add more status codes
        if response.status in NO_RESP_BODY_STATUSES:
            dont_render = True

        if not dont_render:
            if issubclass(type(request.route_data), dict):
                # mapping object, see if we could get the hint...
                render_in = request.route_data.get('render_in', None)

            if render_in is None:
                raise TypeError(
                        "Rendering is not suppressed, but don't know "
                        "where to get rendering instruction!"
                        )

            # rendering is not suppressed, do it now
            cont, extras = render_hub.render_view(
                    request.callback_info[0],
                    response.content,
                    ctx,
                    render_in,
                    )

            if 'mimetype' in extras:
                # Allow renderers to override mimetype
                mime = extras['mimetype']
            else:
                if mime is None:
                    mime = ctx.get('mimetype', 'text/html')

            # encode content, if it's a Unicode thing
            response.content = smartbytes(cont, enc, 'replace')

        # TODO: convert more context into HTTP headers as much as possible
        # generate Content-Type from mimetype and charset
        # but don't append charset if the response is a raw file
        if response.is_raw_file:
            contenttype = mime
        else:
            contenttype = '%s; charset=%s' % (mime, enc, )

        if not dont_render:
            hdrs.append((b'Content-Type', contenttype, ))

        # generate Set-Cookie from cookies
        for cookie_line in ctx.get('cookies', []):
            hdrs.append((b'Set-Cookie', cookie_line, ))

        # 405 Not Allowed header
        if response.status == 405:
            hdrs.append((b'Allow', ctx['allowed_methods'], ))

        response.http_headers = hdrs
        response._dont_render = dont_render

        return response


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
