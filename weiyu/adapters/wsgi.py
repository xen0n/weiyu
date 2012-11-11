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

from functools import partial
from urlparse import parse_qs

from ..helpers.misc import smartstr, smartbytes

from ..registry.provider import request as reg_request

from ..reflex.classes import BaseReflex, ReflexRequest, ReflexResponse
from ..router import router_hub
from ..session import session_hub
from ..rendering.view import render_view_func

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

        # Initial session integration *in reflex*
        # prior to this sessions were per-view, which is obviously a design
        # mistake.
        ses_conf = self.SITE_CONF['session']
        ses_backend, ses_opts = ses_conf['backend'], ses_conf['options']
        self.session = session_hub.do_handling(ses_backend, ses_opts)

    def _do_accept_request(self, env, start_response):
        return WSGIRequest(env, start_response, self.SITE_CONF)

    def _do_translate_request(self, request):
        # populate some useful fields using WSGI env
        env = request.env
        # decode the path bytestring
        # TODO: improve encoding handling here
        request.path = smartstr(env['PATH_INFO'], 'utf-8', 'replace')

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
        request.remote_addr = smartstr(env['REMOTE_ADDR'])
        method = request.method = smartstr(env['REQUEST_METHOD'])
        length, _env_length = None, None
        try:
            _env_length = smartstr(env['CONTENT_LENGTH'], 'ascii', 'ignore')
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

            # parse the POSTed data
            ctype = request.content_type = env.get('CONTENT_TYPE', None)
            if ctype == 'application/x-www-form-urlencoded':
                # decode the response for the view
                form = parse_qs(request.content)

                # eliminate all those 1-element lists
                for k in form.iterkeys():
                    if len(form[k]) == 1:
                        form[k] = form[k][0]

                request.form = form
        else:
            request.content = None

        # TODO: add more ubiquitous HTTP request headers

        # Session injection
        self.session.preprocess(request)

        return request

    def _do_generate_response(self, request):
        fn, args, kwargs = request.callback_info
        response = fn(request, *args, **kwargs)

        # Session persistence is part of generation; may be moved tho
        response = self.session.postprocess(response)

        return response

    def _do_postprocess(self, response):
        # Render the response early
        # TODO: find a way to extract all the literals out
        request = response.request
        ctx, hdrs, extras = response.context, [], {}
        render_in = cont = mime = None
        dont_render = False

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
            cont, extras = render_view_func(
                    request.callback_info[0],
                    response.content,
                    ctx,
                    render_in,
                    )

        enc = ctx.get('enc', 'utf-8')
        response.encoding = enc
        if 'mimetype' in extras:
            # Allow renderers to override mimetype
            mime = extras['mimetype']
        else:
            mime = ctx.get('mimetype', 'text/html') if mime is None else mime

        # encode content, if it's a Unicode thing
        response.content = smartbytes(cont, enc, 'replace')

        # TODO: convert more context into HTTP headers as much as possible
        # generate Content-Type from mimetype and charset
        # but don't append charset if the response is a raw file
        if response.is_raw_file:
            contenttype = mime
        else:
            contenttype = '%s; charset=%s' % (mime, enc, )
        hdrs.append((b'Content-Type', contenttype, ))

        # generate Set-Cookie from cookies
        for cookie_line in ctx.get('cookies', []):
            hdrs.append((b'Set-Cookie', cookie_line, ))

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

        # insert a Content-Length along if response is not raw file
        if not response.is_raw_file:
            headers.append((b'Content-Length', str(len(content)), ))

        for k, v in response.http_headers:
            headers.append((smartbytes(k, enc), smartbytes(v, enc), ))

        # Initiate the actual conversation
        start_response(status_line, headers)

        if response.is_raw_file:
            # push raw file using file_wrapper if provided
            # if one is absent, use a dummy one instead
            raw_fp, raw_blksz = response.raw_fp, response.raw_blksz

            if 'wsgi.file_wrapper' in request.env:
                file_wrapper = request.env['wsgi.file_wrapper']
            else:
                def dummy_file_wrapper(fp, blk_sz=None):
                    blk_sz = blk_sz if blk_sz is not None else 4096
                    do_read = partial(fp.read, blk_sz)
                    chunk = do_read()
                    while len(chunk) > 0:
                        yield chunk
                        chunk = do_read()
                file_wrapper = dummy_file_wrapper

            if raw_blksz is None:
                return file_wrapper(raw_fp)
            else:
                return file_wrapper(raw_fp, raw_blksz)
        else:
            return _send_content(content, enc)


def _send_content(content, enc):
    if isinstance(content, (str, unicode, )):
        yield smartbytes(content, enc, 'replace')
    else:
        for chunk in content:
            # encode and send the chunk using response.encoding
            yield smartbytes(chunk, enc, 'replace')


class WeiyuWSGIAdapter(object):
    def __init__(self):
        self.reflex = WSGIReflex()

    def __call__(self, env, start_response):
        return self.reflex.stimulate(env, start_response)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
