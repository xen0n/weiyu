#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / routing config / grammar
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

from __future__ import unicode_literals, division, print_function

__all__ = [
        'parser',
        ]

import re
import json
from collections import OrderedDict

import ply.yacc as yacc

from .wrlex import WRLexer
tokens = WRLexer.tokens


# general rule
def p_routedef(p):
    '''routedef : attriblist
                | attriblist targetlist
                | attriblist targetlist EOF'''
    attriblist = p[1]
    has_targets = len(p) > 2

    if len(attriblist) == 1:
        p[0] = p[1] + p[2] if has_targets else p[1]
    else:
        # wrap the attribs so that they always occupy 1 position
        p[0] = [p[1]] + p[2] if has_targets else [p[1]]
    #print 'new routedef %s' % (repr(p[0]), )


# ATTRIB list
def p_attriblist_list(p):
    'attriblist : attriblist attribdef NEWLINE'
    p[0] = p[1] + [p[2]]
    #print 'new attriblist:', p[0]


def p_attriblist_def(p):
    'attriblist : attribdef NEWLINE'
    p[0] = [p[1]]
    #print 'new attriblist:', p[0]


def p_attribdef(p):
    'attribdef : ATTRIB'
    p[0] = p[1][2:]
    #print 'ATTRIB: %s' % (repr(p[0]), )


# route target list
def p_targetlist_list(p):
    'targetlist : targetlist targetdeflf'
    p[0] = p[1] + [p[2]]
    #print 'new targetlist: %s' % (repr(p[0]), )


def p_targetlist_def(p):
    'targetlist : targetdeflf'
    p[0] = [p[1]]
    #print 'new targetlist: %s' % (repr(p[0]), )


def p_targetdef_lf(p):
    '''targetdeflf : targetdef
                   | targetdef NEWLINE'''
    p[0] = p[1]


def p_targetdef_simple(p):
    'targetdef : simpletgt'
    p[0] = p[1]


def p_targetdef_router(p):
    'targetdef : subrouter'
    p[0] = p[1]


# regular routing target
def p_simpletgt_simple(p):
    'simpletgt : pattern endpoint renderer'
    p[0] = [p[1], p[2], p[3], ]
    #print 'SIMPLETGT: %s' % (repr(p[0]), )


def p_simpletgt_defaultrenderer(p):
    'simpletgt : pattern endpoint'
    p[0] = [p[1], p[2], {'render_in': 'inherit', }, ]


def p_simpletgt_withextras(p):
    'simpletgt : pattern endpoint renderer extras'
    renderer = p[3]
    extras = p[4]

    if renderer is None:
        p[0] = [p[1], p[2], p[4], ]
    else:
        # renderer is a dictionary
        # NOTE: assertion that the extra data is also a dictionary
        new_extras = renderer.copy()
        new_extras.update(extras)
        p[0] = [p[1], p[2], new_extras, ]


# sub router declaration
def p_subrouter_simple(p):
    'subrouter : pattern COLON INDENT routedef cdedent'
    p[0] = [p[1], p[4], None, ]


def p_subrouter_withextras(p):
    'subrouter : pattern extras COLON INDENT routedef cdedent'
    p[0] = [p[1], p[5], p[2], ]
    #print 'SUBROUTER: %s' % (repr(p[0]), )


# primitives
def p_pattern(p):
    'pattern : LITERAL'
    p[0] = p[1]


def p_endpoint(p):
    'endpoint : LITERAL'
    p[0] = p[1]


def p_renderer(p):
    'renderer : LITERAL'
    p[0] = None if p[1] == 'null' else {'render_in': p[1]}


def p_extras(p):
    'extras : LITERAL'
    p[0] = json.loads(p[1])


# helpers
def p_combined_dedent(p):
    '''cdedent : DEDENT
               | NEWLINE DEDENT'''
    pass


def p_error(tok):
    import sys

    # TODO: proper error recovery
    print('*** Error: %s' % (repr(tok), ), file=sys.stderr)


# don't write parse table, the overhead is negligible when compared to
# the total uptime of web servers
parser = yacc.yacc(debug=0, write_tables=0)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
