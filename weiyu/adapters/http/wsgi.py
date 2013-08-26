#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / adapter / http / WSGI interface
#
# Copyright (C) 2012-2013 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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

from .. import adapter_hub

from ...helpers.misc import smartstr
from ...registry.provider import request as reg_request
from ...reflex.classes import ReflexRequest

from .base import BaseHTTPReflex
from .util import status_to_str, dummy_file_wrapper, send_content_iter
from .util import parse_form, gen_http_headers


class WSGIRequest(ReflexRequest):
    def __init__(self, env, start_response, site_conf):
        super(WSGIRequest, self).__init__(env)

        self.start_response = start_response
        self.site = site_conf


class WSGIReflex(BaseHTTPReflex):
    def __init__(self):
        super(WSGIReflex, self).__init__()

    def _do_accept_request(self, env, start_response):
        return WSGIRequest(env, start_response, self.SITE_CONF)

    def _do_translate_request(self, request):
        # populate some useful fields using WSGI env
        env = request.env
        # decode the path bytestring
        # TODO: improve encoding handling here
        path = request.path = smartstr(env['PATH_INFO'], 'utf-8', 'replace')

        # Move routing (much) earlier so we don't waste time in processing
        # requests impossible to fulfill.
        # Note that we don't pass in "request" at this moment. The object
        # can be replaced by potential hooks, and we certainly don't want
        # a reference to be frozen in the request.
        # Return value is of format (fn, args, kwargs, route_data, )
        route_result = self._do_routing(path)
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
            request.form = parse_form(ctype, request.content)
        else:
            request.content = None

        # TODO: add more ubiquitous HTTP request headers

        # do session injection in baseclass
        return super(WSGIReflex, self)._do_translate_request(request)

    def _do_deliver_response(self, response):
        if response._vanished:
            # We've been hijacked. Nothing should be done.
            return

        content = response.content
        status_code = response.status
        enc = response.encoding

        request = response.request

        # Initiate the actual conversation
        request.start_response(*gen_http_headers(response))

        if response.is_raw_file:
            # push raw file using file_wrapper if provided
            # if one is absent, use a dummy one instead
            raw_fp, raw_blksz = response.raw_fp, response.raw_blksz

            if 'wsgi.file_wrapper' in request.env:
                file_wrapper = request.env['wsgi.file_wrapper']
            else:
                file_wrapper = dummy_file_wrapper

            if raw_blksz is None:
                return file_wrapper(raw_fp)
            else:
                return file_wrapper(raw_fp, raw_blksz)
        else:
            return send_content_iter(content, enc)


class WeiyuWSGIAdapter(object):
    def __init__(self):
        self.reflex = WSGIReflex()

    def __call__(self, env, start_response):
        return self.reflex.stimulate(env, start_response)


@adapter_hub.register_handler('wsgi')
def wsgi_adapter_factory(hub):
    return WeiyuWSGIAdapter()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
