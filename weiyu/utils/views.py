#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / utilities / useful views
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

from __future__ import unicode_literals, division

from os.path import exists, isdir, islink, normcase
from os.path import normpath, abspath, realpath, join as pathjoin
from mimetypes import guess_type

from ..reflex.classes import ReflexResponse
from ..router import router_hub


@router_hub.endpoint('wsgi', 'staticfile')
def staticfile_view(request, path):
    # TODO: caching
    conf = request.SITE_CONF['staticfile']
    STATIC_ROOT = normcase(conf['root'])

    # XXX WARNING From here SECURITY IS VERY IMPORTANT!!
    # first do NOT let ANY '..' things pass thru by forcing a normalization
    norm_relpath = normpath('/' + path)

    # concat the normalized thing and STATIC_ROOT together
    # XXX Here any potential symlink is a security hole! Production
    # environment should NEVER use this view; instead PLEASE rely on the
    # web server to do the job!
    real_path = realpath(abspath(pathjoin(STATIC_ROOT, norm_relpath)))
    real_path = normcase(real_path)

    if exists(real_path) and not isdir(real_path):
        # decide mimetype solely by using filename
        # mimetype is either a bytestring or None
        mimetype, enc_prog = guess_type(real_path)
        if mimetype is None:
            # fallback to binary stream
            mimetype = 'application/octet-stream'

        # we should prepare a file pointer
        fp = open(real_path, 'rb')

        # return a raw file response
        return ReflexResponse(
                200,
                {'sendfile_fp': fp, },
                {'is_raw_file': True, 'mimetype': mimetype, },
                request,
                )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
