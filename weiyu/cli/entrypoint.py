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

# Argument parser setup
parser = argparse.ArgumentParser(
        description='Command-line utility for weiyu.',
        )

# Rainfile path
parser.add_argument('-c', '--config', help='path of Rainfile to use')

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


def main():
    # Fix up sys.path to include the current directory, similar to what a
    # regular script would have.
    sys.path.insert(0, os.path.realpath('.'))

    args = parser.parse_args()
    return args.func(args)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
