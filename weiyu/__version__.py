#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / top-level package / package version file
#
# Copyright (C) 2012 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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

# NOTE: the SVN support code reused Django project's.

from __future__ import unicode_literals, division

__all__ = ['VERSION_MAJOR', 'VERSION_MINOR', 'VERSION_REV',
           'VERSION', 'VERSION_DEV', 'VERSION_STR',
           ]

import os.path
from sys import getfilesystemencoding
import re
import weiyu as __this_pkg

# Caveat: this file is imported also by setup.py, so we can't guarantee
# six's presence! This can lead package installation to fail.
# import six
#
# Instead, make up ourselves the only feature we need here -- six.text_type,
# which is very easy to implement...
text_type = str if __import__('sys').version_info[0] == 3 else unicode


# Version information.
VERSION_MAJOR = 0
VERSION_MINOR = 3
VERSION_REV = 0

VERSION = (VERSION_MAJOR, VERSION_MINOR, VERSION_REV, 'alpha', 0)

_VCS_HANDLERS = []


def get_version(use_dev_suffix=True):
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        if use_dev_suffix:
            version = '%s-dev' % version
    else:
        if VERSION[3] != 'final':
            version = '%s %s %s' % (version, VERSION[3], VERSION[4])

    return version


def _get_git_commit(path=None):
    '''Returns the Git commit hash truncated after the 7th hex digit, ``None``
    if anything goes wrong.

    If path is provided, it should be a directory whose Git info you want
    to inspect. If it's not provided, this will use the root package
    directory's parent dir.

    '''

    # Git directory...
    if path is None:
        path = __this_pkg.__path__[0]
        git_path = '%s/../.git/' % path
    else:
        git_path = '%s/.git/' % path

    # normalize a little bit
    git_path = os.path.normpath(git_path)

    # Phase 1, read the HEAD file to get the current head
    head_path = os.path.join(git_path, 'HEAD')
    try:
        with open(head_path, 'rb') as fp:
            ref = fp.read().strip().decode('ascii', 'replace')
    except IOError:
        return None
    else:
        ref_path_match = re.search(r'^ref: (.*)$', ref)
        if ref_path_match:
            ref_path = ref_path_match.groups()[0]
        else:
            # unrecognized HEAD format...
            return None

    # now ref_path is ready, move on to Phase 2, pull out the commit id
    commit_path = os.path.normpath(os.path.join(git_path, ref_path))
    try:
        with open(commit_path, 'rb') as fp:
            commit = fp.read().strip().decode('ascii', 'replace')
    except IOError:
        return None
    else:
        # Truncate the commit id.
        commit_id = commit[:7]

    # if we arrive here, we're done and commit id is ready.
    return commit_id


# read the Git commit hash if available
_vcs_rev = _get_git_commit()

# init our version strings... they are constant during one run
VERSION_DEV = _vcs_rev or ''
VERSION_STR = (
        '%s-g%s'  % (get_version(False), _vcs_rev, )
        if _vcs_rev
        else get_version(True)
        )

del _vcs_rev


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
