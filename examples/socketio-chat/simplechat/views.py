#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / hello world app - view
#
# This file is in public domain.

from __future__ import unicode_literals, division

from weiyu.shortcuts import http, renderable, view


@http('index')
@renderable('mako', 'index.html')
@view
def index_view(request):
    return (
            200,
            {},
            {
                'mimetype': 'text/html',
                'enc': 'utf-8',
                },
            )


@http('404')
@renderable('mako', '404.html')
@view
def http404_view(request):
    return (
            404,
            {},
            {
                'mimetype': 'text/html',
                'enc': 'utf-8',
                },
            )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
