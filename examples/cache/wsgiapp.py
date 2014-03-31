#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / Cache integration - WSGI stub
#
# This file is in public domain.

from __future__ import unicode_literals

from weiyu.init import inject_app

inject_app()


if __name__ == '__main__':
    from weiyu.utils.server import cli_server
    cli_server('cherrypy')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
