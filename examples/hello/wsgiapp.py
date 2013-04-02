#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / hello world app - WSGI file
#
# This file is in public domain.

from __future__ import unicode_literals, division

from weiyu.shortcuts import *
from weiyu.utils.server import cli_server

# initialize registries, views, router and app, in that order
load_config('conf.json')
load_views('views.json')
load_router('http', 'urls.txt')
application = make_app('wsgi')


if __name__ == '__main__':
    cli_server('cherrypy')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
