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


from cgi import escape

from ..__version__ import VERSION_STR
from ..registry.provider import request, _registries as REGS
from ..reflex.classes import BaseReflex


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

OUTPUT_ENC = 'utf-8'

# TODO: put some REAL stuff here when enough infrastructure is in place!
PLACEHOLDER = ('''\
<!DOCTYPE html>
<html>
    <head>
        <title>Test drive - %%(sitename)s</title>

        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

        <style type="text/css">
/* YUI RESET */
html{color:#000;}body,div,dl,dt,dd,ul,ol,li,h1,h2,h3,h4,h5,h6,pre,code,form,fieldset,legend,input,button,textarea,select,p,blockquote,th,td{margin:0;padding:0}table{border-collapse:collapse;border-spacing:0}fieldset,img{border:0}address,button,caption,cite,code,dfn,em,input,optgroup,option,select,strong,textarea,th,var{font:inherit}del,ins{text-decoration:none}li{list-style:none}caption,th{text-align:left}h1,h2,h3,h4,h5,h6{font-size:100%%%%;font-weight:normal}q:before, q:after {content:''}abbr,acronym{border:0;font-variant:normal}sup{vertical-align:baseline}sub{vertical-align:baseline}legend{color:#000}a{text-decoration:none;color:inherit}

html {
    background-color: #333;
    font-family: "Segoe UI Light", "WenQuanYi Micro Hei", "Sans", "Arial", sans-serif;
}

body {
    background-color: #ccc;
}

a {
    text-decoration: underline;
}

div.root {
    margin: 0 16px;
    font-size: 16px;
}

div.header {
    margin: 0 0 32px;
    padding: 16px 0 0;
}

div.header h1 {
    display: inline-block;
    color: #111;
    font-size: 54px;
    font-weight: 200;
    text-shadow: 0 1px 0 #fff;

    padding: 0 64px 8px 0;
    border-bottom: 1px solid #999;
}

div.content {
    color: #333;
    margin: 0 0 64px;
    line-height: 1.75;
}

div.content p {
    font-weight: 200;

    margin: 0 0 16px;
    padding-left: 32px;
    border-left: 2px solid #999;
}

div.content table.env {
    margin: 0 auto;
    max-width: 1000px;
}

div.content table.env thead {
    background-color: rgba(0, 0, 0, 0.1);
    border-bottom: 1px solid #333;
}

div.content table.env tbody {
    font-family: "Courier New", "WenQuanYi Micro Hei Mono", "Monospace", monospace;
}

div.content table.env tbody tr:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

div.content table.env td {
    padding: 3px;
}

div.footer {
    color: #999;
    background-color: #333;

    font-size: 12px;
    font-weight: 100;
    text-align: center;
    text-shadow: 0 1px 0 #111;

    padding: 8px 0 0;
}

div.footer p {
    line-height: 1.5;
    margin: 0 0 8px;
}
        </style>
    </head>

    <body>
        <div class="root">
            <div class="header">
                <h1>weiyu worked (almost)</h1>
            </div>

            <div class="content">
                <p>
                    You are viewing a placeholder page.
                    Infrastructure is not fully built up yet.
                    So this site doesn't do anything real other than
                    displaying this boring placeholder.
                </p>

                <p>
                    Anyway, plz stay tuned.<br />
                    Wish you a good day.
                </p>

                <p>
                    Here is the complete WSGI environment for the request,
                    which can possibly help you figure out more about your
                    WSGI configuration.
                </p>

                <table class="env">
                    <thead>
                        <tr>
                            <td>Key</td>
                            <td>Value</td>
                        </tr>
                    </thead>

                    <tbody>
%%(env)s
                    </tbody>
                </table>

                <p>
                    Here is the weiyu registry:
                </p>

                <table class="env">
                    <thead>
                        <tr>
                            <td>Reg</td>
                            <td>Key</td>
                            <td>Value</td>
                        </tr>
                    </thead>

                    <tbody>
%%(regs)s
                    </tbody>
                </table>
            </div>
        </div>

        <div class="footer">
            <p>
                powered by
                <a href="https://github.com/xen0n/weiyu/">weiyu</a>
                %(version)s
            </p>

            <p>
                <a href="http://validator.w3.org/check?uri=referer">
                    valid HTML5
                </a>
            </p>
        </div>
    </body>
</html>
''' % {
        'version': VERSION_STR,
        }).encode(OUTPUT_ENC)

ENV_TEMPLATE = '''\
                        <tr>
                            <td>%(k)s</td>
                            <td>%(v)s</td>
                        </tr>
'''.encode(OUTPUT_ENC)

REG_TEMPLATE = '''\
                        <tr>
                            <td>%(n)s</td>
                            <td>%(k)s</td>
                            <td>%(v)s</td>
                        </tr>

'''.encode(OUTPUT_ENC)


def make_one_env_row(k, v):
    html_k = escape(k).encode('ascii', 'xmlcharrefreplace')
    html_v = escape(repr(v)).encode('ascii', 'xmlcharrefreplace')

    return ENV_TEMPLATE % {'k': html_k, 'v': html_v, }


def make_env_entries(env):
    return b''.join(make_one_env_row(k, v) for k, v in sorted(env.items()))


def make_reg_entries(name, reg):
    name = name.encode(OUTPUT_ENC)
    tmp = []

    for k, v in reg.items():
        html_k = escape(k).encode('ascii', 'xmlcharrefreplace')
        html_v = escape(repr(v)).encode('ascii', 'xmlcharrefreplace')

        tmp.append(REG_TEMPLATE % {'n': name, 'k': html_k, 'v': html_v, })

    return b''.join(tmp)

def make_regs_entries():
    tmp = []
    for name, reg in REGS.items():
        tmp.append(make_reg_entries(name, reg))

    return b'\n'.join(tmp)


def get_response(env, conf):
    return PLACEHOLDER % {
            'env': make_env_entries(env),
            'regs': make_regs_entries(),
            'sitename': conf['name'].encode(OUTPUT_ENC),
            }


class WSGIRequest(object):
    def __init__(self, env, start_response, site_conf):
        self.environ = env
        self.start_response = start_response
        self.site = site_conf

        # populate some useful fields using WSGI env
        self.populate()

    def populate(self):
        # TODO
        pass


# TODO: rewrite to an adapter-agnostic form, and inherit from that
class WSGIResponse(object):
    def __init__(self, status, headers, content, request):
        self.status = status
        self.headers = headers
        self.content = content
        self.request = request


class WSGIReflex(BaseReflex):
    def __init__(self, worker_func):
        self.SITE_CONF = request('site')
        self.worker_func = worker_func

    def _do_accept_request(self, env, start_response):
        return WSGIRequest(env, start_response, self.SITE_CONF)

    def _do_generate_response(self, request):
        status, headers, content = self.worker_func(request)
        return WSGIResponse(status, headers, content, request)

    def _do_deliver_response(self, response):
        content = response.content
        status_code = response.status

        request = response.request
        start_response = request.start_response

        status_line = b'%d %s' % (
                status_code,
                STATUS_CODES_MAP[status_code],
                )

        headers = [
                (k.encode(OUTPUT_ENC), v.encode(OUTPUT_ENC), )
                for k, v in response.headers.iteritems()
                ]

        start_response(status_line, headers)

        if isinstance(content, (str, unicode, )):
            yield content
        else:
            for chunk in content:
                yield chunk


class WeiyuWSGIAdapter(object):
    def __init__(self, worker_func):
        self.reflex = WSGIReflex(worker_func)

    def __call__(self, env, start_response):
        return self.reflex.stimulate(env, start_response)


# XXX TEST CODE, TO BE FACTORED OUT
def env_test_worker(request):
    return (
            200,
            {'Content-Type': 'text/html; charset=utf-8', },
            iter([get_response(request.environ, request.site), ]),
            )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
