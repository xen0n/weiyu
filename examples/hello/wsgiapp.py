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
# NOTE: Currently PyYAML exclusively return bytestrings instead of
# Unicode strings for string elements, at least on Python 2.x, so
# don't be surprised if your config file contains Unicode characters
# and the config seems to be garbled.
inject_app()


if __name__ == '__main__':
    cli_server('cherrypy')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
