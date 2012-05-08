#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / adater / WSGI interface
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

from weiyu.__version__ import VERSION_STR


# TODO: put some REAL stuff here when enough infrastructure is in place!
PLACEHOLDER = ('''\
<!DOCTYPE html>
<html>
    <head>
        <title>weiyu test page</title>

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
''' % {'version': VERSION_STR, }).encode('utf-8')

ENV_TEMPLATE = '''\
                        <tr>
                            <td>%(k)s</td>
                            <td>%(v)s</td>
                        </tr>
'''.encode('utf-8')


def make_one_env_row(k, v):
    htmlsafe_k = escape(k).encode('ascii', 'xmlcharrefreplace')
    htmlsafe_v = escape(repr(v)).encode('ascii', 'xmlcharrefreplace')

    return ENV_TEMPLATE % {'k': htmlsafe_k, 'v': htmlsafe_v, }


def make_env_entries(env):
    return b''.join(make_one_env_row(k, v) for k, v in sorted(env.items()))


def get_response(env):
    return PLACEHOLDER % {'env': make_env_entries(env), }


class WeiyuWSGIAdapter(object):
    def __call__(self, env, start_response):
        start_response(b'200 OK', [(b'Content-Type', b'text/html'), ])
        yield get_response(env)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
