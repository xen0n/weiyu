#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / command line / entry point
#
# Copyright (C) 2014 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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

import sys
import os
import argparse

from .commands import shell
from .commands import serve

# Argument parser setup
parser = argparse.ArgumentParser(
        description='Command-line utility for weiyu.',
        )

# Rainfile path
parser.add_argument('-c', dest='config', help='path of Rainfile to use')
parser.add_argument(
        '--across-fs',
        action='store_true',
        help='discover project config across FS boundary',
        )

# Sub-commands
subparsers = parser.add_subparsers(
        title='subcommands',
        )

# rain shell
parser_shell = subparsers.add_parser(
        'shell',
        help='Open a Python shell with weiyu initialized',
        )
parser_shell.set_defaults(func=shell.rain_shell)

# rain serve
parser_serve = subparsers.add_parser(
        'serve',
        help='Fire up development server',
        )
parser_serve.add_argument(
        '-f',
        '--server-flavor',
        help='flavor of server',
        default='cherrypy',
        )
parser_serve.add_argument(
        '-t',
        '--adapter-type',
        help='type of adapter to use',
        default='wsgi',
        )
parser_serve.add_argument(
        '-p',
        '--port',
        help='port to listen on',
        type=int,
        default=9090,
        )
parser_serve.set_defaults(func=serve.rain_serve)


def main():
    # Fix up sys.path to include the current directory, similar to what a
    # regular script would have.
    sys.path.insert(0, os.path.realpath('.'))

    args = parser.parse_args()
    return args.func(args)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
