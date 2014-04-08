#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / utilities / Sphinx extension
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

from docutils import nodes

from ..helpers.misc import smartstr
from ..router import router_hub


def app_from_inliner(inliner):
    return inliner.document.settings.env.app


def reverser_from_config(app):
    try:
        return router_hub.reverser_for(app.config.weiyu_router_type)
    except KeyError as e:
        raise ValueError("requested router type '%s' unknown" % (e, ))


def get_reverse_url(app, ep):
    reverser = reverser_from_config(app)

    # This will raise ValueError's when errors happen, just what we want here.
    return reverser.signature(ep)


def make_reverse_url_node(app, rawtext, text):
    ep = text.strip()
    signature = get_reverse_url(app, ep)
    return nodes.literal(rawtext, signature[0])


def wyurl_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    '''Automatically reverse the endpoint given and show the URL signature.

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.  Both are allowed to be
    empty.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.

    '''

    app = app_from_inliner(inliner)

    try:
        return [make_reverse_url_node(app, rawtext, text)], []
    except ValueError as e:
        msg = inliner.reporter.error(
                'URL reverse resolution error: %s' % (smartstr(e.message), ),
                line=lineno,
                )
        prb = inliner.problematic(rawtext, rawtext, msg)

        return [prb], [msg]


def setup(app):
    app.add_role('wyurl', wyurl_role)
    app.add_config_value('weiyu_router_type', 'http', 'env')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
