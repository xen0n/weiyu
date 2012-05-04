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
html{color:#000;}body,div,dl,dt,dd,ul,ol,li,h1,h2,h3,h4,h5,h6,pre,code,form,fieldset,legend,input,button,textarea,select,p,blockquote,th,td{margin:0;padding:0}table{border-collapse:collapse;border-spacing:0}fieldset,img{border:0}address,button,caption,cite,code,dfn,em,input,optgroup,option,select,strong,textarea,th,var{font:inherit}del,ins{text-decoration:none}li{list-style:none}caption,th{text-align:left}h1,h2,h3,h4,h5,h6{font-size:100%%;font-weight:normal}q:before, q:after {content:''}abbr,acronym{border:0;font-variant:normal}sup{vertical-align:baseline}sub{vertical-align:baseline}legend{color:#000}a{text-decoration:none;color:inherit}

html {
    background-color: #333;
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
    text-shadow: 0 1px 0 #fff;

    padding: 0 64px 8px 0;
    border-bottom: 1px solid #999;
}

div.content {
    color: #333;
    margin: 0 0 64px;
}

div.content p {
    line-height: 1.75;
    font-weight: 200;

    margin: 0 0 16px;
    padding-left: 32px;
    border-left: 2px solid #999;
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


class WeiyuWSGIAdapter(object):
    def __call__(self, env, start_response):
        start_response(b'200 OK', [(b'Content-Type', b'text/html'), ])
        yield PLACEHOLDER


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
