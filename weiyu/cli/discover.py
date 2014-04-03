#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / command line / config discovery
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

from __future__ import unicode_literals, print_function

import sys
import os

from .. import init


def check_config_path(path):
    # Rain.d
    if os.path.isdir(os.path.join(path, 'Rain.d')):
        return path

    # Rainfile.yml (old default)
    if os.path.isfile(os.path.join(path, 'Rainfile.yml')):
        return path

    # conf.yml, conf.json are long deprecated, let's not support them...
    return None


def discover_config(path, cross_filesystem):
    # Traverse upwards, until at filesystem boundary or /, or we've found the
    # correct base directory.
    tmp = path
    while True:
        if check_config_path(tmp):
            return 0, tmp

        if os.path.ismount(tmp) and not cross_filesystem:
            # Base directory not found, stop at filesystem boundary.
            print(
                    'fatal: No Rain.d or Rainfile.yml found (or any parent '
                    'up to mount point {0})\n'
                    'Stopping at filesystem boundary (--discovery-across-fs '
                    'not set).'.format(tmp),
                    file=sys.stderr,
                    )

            return 128, None

        new_tmp = os.path.realpath(os.path.join(tmp, '..'))
        if tmp == new_tmp:
            # Infinite recursion, maybe we've run into / or some circular
            # linked directories...
            print(
                    'fatal: No Rain.d or Rainfile.yml found (or any of the '
                    'parent directories)',
                    file=sys.stderr,
                    )

            return 128, None

        tmp = new_tmp


def auto_discover_and_init(cross_filesystem):
    cwd = os.getcwdu()
    retcode, project_root = discover_config(cwd, cross_filesystem)
    if project_root is None:
        return retcode

    if project_root != cwd:
        print(
                ' * Using project directory: {0}\n'.format(project_root),
                file=sys.stderr,
                )

    # init framework
    try:
        if project_root != cwd:
            os.chdir(project_root)

            # add project root to sys.path
            sys.path.insert(0, os.path.realpath(project_root))

        init.boot()
    finally:
        if project_root != cwd:
            os.chdir(cwd)

    return 0


def init_or_die(args):
    if args.config is not None:
        # use override config
        init.boot(args.config)
        return

    # do auto discovery
    ret = auto_discover_and_init(args.discovery_across_fs)
    if ret != 0:
        sys.exit(ret)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
