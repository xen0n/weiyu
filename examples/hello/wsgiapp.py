#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / hello world app - WSGI file
#
# This file is in public domain.

from __future__ import unicode_literals, division

from weiyu.shortcuts import *
from weiyu.utils.server import cli_server

# load up registries
load_config('conf.json')

# load views
load_views('views.json')

# init router and app
load_router('http', 'urls.txt')
application = make_app('wsgi')


if __name__ == '__main__':
    cli_server('cherrypy')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
