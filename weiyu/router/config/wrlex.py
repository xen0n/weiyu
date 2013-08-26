#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / routing config / lexer
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

import re
from collections import OrderedDict

import six


class Token(object):
    def __init__(self, type, data, span, line):
        self.type = type
        self.value = data
        self.span = span
        self.line = line

    def __repr__(self):
        return '%d, %d-%d Token(%s, %s)' % (
                self.line,
                self.span[0],
                self.span[1],
                self.type,
                repr(self.value),
                )


class Lexer(object):
    def __init__(self, s=None):
        self._lex_reset(s)

    def _lex_reset(self, s):
        self._pos = 0
        self._lineno = 1

        if s is not None:
            self._input = s
            self._length = len(s)

        self._tokens = None
        self._state = 'INITIAL'
        self._prev = None
        self._ply_pos = None

    def input(self, s):
        self._lex_reset(s)

    def get_token(self, type, frag, match):
        span = match.span()
        return Token(type, frag, span, self._lineno)

    def eof(self):
        return self._pos >= self._length

    def lex(self):
        cls = self.__class__

        _rule_cache = OrderedDict(
                (name, re.compile(rule), )
                for name, rule in six.iteritems(cls.RULES)
                )
        _handlers = {
                name: getattr(self, 't_%s' % name)
                for name in six.iterkeys(_rule_cache)
                }

        self._tokens = []
        while self._pos <= self._length:
            matched = False
            for name, rule in six.iteritems(_rule_cache):
                match = rule.match(self._input, self._pos)
                if match is not None:
                    matched = True
                    match_span = match.span()
                    # advance the pointer
                    self._pos = match_span[1]

                    # generate the token(s)
                    frag = self._input[match_span[0]:match_span[1]]
                    skip, result = _handlers[name](frag, self, match)
                    if skip:
                        continue

                    # print result
                    self._tokens.extend(result)

                    # update previous token
                    self._prev = self._tokens[-1].type
                    break

            if not matched:
                raise ValueError('could not advance any more')

    def token(self):
        # For compatibility with PLY.
        if self._ply_pos is None:
            self._ply_pos = 0
            if self._tokens is None:
                # lex first
                self.lex()
        if self._ply_pos >= len(self._tokens):
            return None

        pos = self._ply_pos
        self._ply_pos += 1
        return self._tokens[pos]


class WRLexer(Lexer):
    RULES = OrderedDict([
            ('ATTRIB', r'--[^\s]+'),
            ('NEWLINE', r'\n+'),
            ('SPACE', r'[ \t]*'),
            ('COLON', r':\n'),
            #('LITERAL', r'(?:[^\s]*\\\s)*[^\s]+'),
            ('LITERAL', r'[^\'\"\s]*[^\'\"\s:]|\'[^\']*\'|\"[^\"]*\"'),
            ('EOF', r'$'),
            ])

    tokens = list(six.iterkeys(RULES)) + ['INDENT', 'DEDENT', ]
    tokens.remove('SPACE')
    tokens = tuple(tokens)

    def __init__(self, *args, **kwargs):
        super(WRLexer, self).__init__(*args, **kwargs)
        self._is_prev_space_empty = False
        self._indent_stack = [0]

    # f for fragment, l for lexer instance, m for match object
    def t_ATTRIB(self, f, l, m):
        return False, [self.get_token('ATTRIB', f, m), ]

    def t_NEWLINE(self, f, l, m):
        l._lineno += len(f)
        return False, [self.get_token('NEWLINE', f, m), ]

    def t_LITERAL(self, f, l, m):
        #return False, [self.get_token('LITERAL', f, m), ]
        actual_frag = f if f[0] not in '\'"' else f[1:-1]
        return False, [self.get_token('LITERAL', actual_frag, m), ]

    def t_SPACE(self, f, l, m):
        # but we certainly don't want to be stuck in an infinite loop, so
        # record the fact if we ARE matching an empty string right now
        if self._is_prev_space_empty:
            self._is_prev_space_empty = False
            return True, None

        if len(f) == 0:
            self._is_prev_space_empty = True

        if not l.eof() and l._input[m.span()[0] - 1] != '\n':
            # we're only interested in leading whitespaces
            # INCLUDING EOF CONDITION
            return False, []

        # try to generate INDENT/DEDENT tokens
        # first let's calculate effective width
        efflen = 0
        for ch in f:
            efflen += (8 - efflen % 8) if ch == '\t' else 1

        indstk = self._indent_stack
        stktop = indstk[-1]

        # same indentation level? if is, return early
        if stktop == efflen:
            return False, []

        # INDENT handling
        if stktop < efflen:
            # indent, push stack
            indstk.append(efflen)
            return False, [self.get_token('INDENT', f, m), ]

        # DEDENT check
        dedents = []
        while stktop > efflen:
            dedents.append(self.get_token('DEDENT', f, m), )
            # pop stack
            indstk.pop()
            stktop = indstk[-1]
        if stktop != efflen:
            # inconsistent indentation, bark
            raise IndentationError('inconsistent indentation')
        # check ok, return
        return False, dedents

    def t_COLON(self, f, l, m):
        return False, [self.get_token('COLON', f, m), ]

    def t_EOF(self, f, l, m):
        # just treat this as whitespace...
        result = self.t_SPACE(f, l, m)
        # but we must make sure the lexing loop terminates!
        l._pos += 1
        return result


if __name__ == b'__main__':
    import sys
    fname = sys.argv[1]
    with open(fname, 'rb') as fp:
        content = fp.read().decode('utf-8')

    m = WRLexer()
    m.input(content)
    while True:
        tok = m.token()
        if tok is None:
            break
        print(tok)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
