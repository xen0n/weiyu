#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / hello world app - WSGI stub
#
# This file is in public domain.

from gevent import monkey; monkey.patch_all()

from weiyu.shortcuts import inject_app
from weiyu.utils.server import cli_server

inject_app()


if __name__ == '__main__':
    cli_server(
            'socketio',
            ('0.0.0.0', 8080),
            resource="socket.io",
            policy_server=True,
            policy_listener=('0.0.0.0', 10843),
            )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
