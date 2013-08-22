#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / hello world app - WSGI stub
#
# This file is in public domain.

from __future__ import unicode_literals, division

from weiyu.init import inject_app
from weiyu.utils.server import cli_server

# For YAML config do this instead:
# inject_app(conf_path='conf.yml')
inject_app()


if __name__ == '__main__':
    cli_server('cherrypy')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
