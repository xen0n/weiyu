#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# weiyu / utilities / KBS system post reader
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

import sys
import re

from os.path import isdir
from os.path import join as pathjoin
from glob import iglob

# Constants.
KBS_POST_ENCODING = 'gb18030'
KBS_SIGNATURE_DELIM = u'--'

OUTPUT_ENCODING = 'utf-8'

# Signature conversion status code.
SIGN_EXACT, SIGN_AMBIGUOUS, SIGN_BLURRY = range(3)

# REs.
KBS_FROM = re.compile(ur'^发信人: (?P<ID>[^ ]+) \((?P<nick>.*?)\)?, '
                      ur'信区: (?P<board>.*)$'
                      )
KBS_TITLE = re.compile(ur'^标  题: (?P<title>.*)$')
KBS_SITE = re.compile(ur'^发信站: (?P<site>.*?) \((?P<date>.*)\), 站内$')
KBS_ADDR = re.compile(ur'\[FROM: (?P<addr>.*)\]')

# Presentation format, for console visual inspection and debugging purposes.
# The keys match those specified in the various parsing functions.
PRES_FORMAT = u'''\
S='%(site)s'
A='%(author)s'
N='%(nickname)s'
B='%(board)s'

I='%(fromaddr)s'
D='%(date)s'
T='%(title)s'
C: (att %(have_att)d)
%(content)s
==========
S: (exactness %(exactness)d)
%(signature)s
==========
'''

STATISTIC_LINE = (u'\rT=%(tot)-6d, A=%(att)-3d, S=%(sys)-3d, E=%(err)-3d, '
                  u'Sl=%(sign)s'
                  )


# Helper routines.
def read_post_lines(name):
    # TODO: Attachment problem!!
    # buf = []
    have_att = False
    with open(name, 'rb') as fp:
        # while True:
        chunk = fp.read()

        null_idx = chunk.find('\x00')
        # print len(chunk)
        if null_idx != -1:
            # null char, assume end
            # buf.append(chunk[:null_idx])
            # break
            content = chunk[:null_idx]
            have_att = True
        # no null's, append whole chunk
        # buf.append(chunk)
        else:
            content = chunk

    # content = ''.join(buf)
    return (content.decode(KBS_POST_ENCODING, 'ignore')
            .strip(u'\n')
            .split(u'\n'),
            have_att,
            )


# Parsing functions.
def parse(lines):
    result = {}

    result.update(parse_header(lines))

    footer, sign_delim_idx = parse_footer(lines)
    result.update(footer)

    # for footerless posts generated by system: check if originating IP is u''
    have_footer = len(footer[u'fromaddr']) != 0

    result.update(extract_content(lines, sign_delim_idx, have_footer))

    return result


# Parsing of the individual parts.
def parse_header(lines):
    from_line, title_line, site_line = lines[:3]

    from_g = KBS_FROM.match(from_line).group
    title_g = KBS_TITLE.match(title_line).group
    site_g = KBS_SITE.match(site_line).group

    # 1st line: author, nickname at the time of post, and board name
    author, nickname, board = from_g(u'ID'), from_g(u'nick'), from_g(u'board')

    # 2nd line: title
    title = title_g(u'title')

    # 3rd line: origin site and date
    site, date = site_g(u'site'), site_g(u'date')

    return {u'author': author,
            u'nickname': nickname,
            u'board': board,
            u'title': title,
            u'site': site,
            u'date': date,
            }


def separate_signature(sign_reverse):
    # KBS imposes a 6-line limitation on signatures, so we can resonably guess
    # where the dividing '--' line is.
    result, delim_count, first_delim = [], 0, 0

    for idx, line in enumerate(reversed(sign_reverse)):
        #print idx, line[:10],
        if line[-2:] == KBS_SIGNATURE_DELIM:
            # '--' or 'xyzabc--' in case of rather casual edits
            delim_count += 1
            #print u'DELIM %d' % delim_count,
            if delim_count == 1:
                # first encounter, record pos in reversed order and skip over
                first_delim = idx - len(sign_reverse) + 1
                #print u'FIRSTDELIM %d' % first_delim
                continue

        # not obviously a delimiter, adding to result
        if delim_count > 0:
            result.append(line)
        #print

    if delim_count == 1:
        # just pretending to be exact, actually...
        return SIGN_EXACT, u'\n'.join(result), first_delim

    if delim_count > 1:
        return SIGN_AMBIGUOUS, u'\n'.join(result), first_delim

    return SIGN_BLURRY, u'', 0


def parse_footer(lines):
    addr_line = lines[-1]
    # reserve 8 lines, that is 6 + 1 delim + 1 possibly blank line
    # Not sure why some people have 7-line sigs...
    sign_zone_reverse = lines[-3:-11:-1]

    # print addr_line
    # NOTE: some system-generated posts like banning an ID don't have footer,
    # we should detect this case and set originating IP to empty.
    fromaddr_m, fromaddr = KBS_ADDR.search(addr_line), u''
    if fromaddr_m is not None:
        fromaddr = fromaddr_m.group(u'addr')
    status, signature, sign_delim_idx = separate_signature(sign_zone_reverse)

    return {u'signature': signature,
            u'exactness': status,
            u'fromaddr': fromaddr,
            }, sign_delim_idx


def extract_content(lines, sign_delim_idx, have_footer):
    # the last 2 lines are always not interesting, with knowledge of signature
    # line count we can finally pull out the content of the post.
    # TODO tackle with the case of 'xxxyyyzzz--' delimiter where the last line
    # of content is in the delimiter line itself

    # -2 plus a -1 removing the delim line
    # for posts lacking footer, we don't discard any line
    if have_footer:
        content_lines = lines[4:sign_delim_idx - 3]
    else:
        content_lines = lines[4:]

    return {u'content': u'\n'.join(content_lines), }


# for presentational and debug purpose
def gen_printout_str(post):
    return (PRES_FORMAT % post).encode(OUTPUT_ENCODING)


# main function
def main(argc, argv):
    if argc < 3:
        print >>sys.stderr, u'usage: %s <mode> <files to inspect>' % argv[0]
        print >>sys.stderr, u'\nmodes:\na -- analyze\ns -- merely print stat'
        print >>sys.stderr, u'd -- same as s, accepting directories'
        return 1

    mode = argv[1]
    if mode == u'a':
        # analyzing posts
        for fname in argv[2:]:
            print "file '%s':" % fname
            post_lines, have_att = read_post_lines(fname)
            try:
                post = parse(post_lines)
            except Exception, e:
                print u'XXX parse error, exc %s' % repr(e)
            else:
                post[u'have_att'] = 1 if have_att else 0
                print gen_printout_str(post)
        return 0

    if mode == u's' or mode == u'd':
        # only print statistical data
        cnt = {u'tot': 0, u'att': 0, u'sys': 0, u'err': 0, u'sign': [0, 0, 0]}
        cnt_sign_exactness = cnt[u'sign']

        iters = []
        if mode == u'd':
            for dname in argv[2:]:
                iters.append(enumerate(iglob(pathjoin(dname, '*'))))
        else:
            iters.append(enumerate(argv[2:]))

        for iterobj in iters:
            for i, fname in iterobj:
                post_lines, have_att = read_post_lines(fname)
                try:
                    post = parse(post_lines)
                except Exception, e:
                    cnt[u'err'] += 1
                    print u"\n'%s': exc %s" % (fname, repr(e), )
                else:
                    if have_att:
                        cnt[u'att'] += 1
                    if len(post[u'fromaddr']) == 0:
                        cnt[u'sys'] += 1
                    cnt_sign_exactness[post[u'exactness']] += 1

                if i % 10 == 0:
                    cnt[u'tot'] = i
                    print >>sys.stderr, STATISTIC_LINE % cnt,

        # final update
        cnt[u'tot'] = i
        print (STATISTIC_LINE.replace(u'\r', u'')) % cnt

        return 0

    # unrecognized mode...
    print >>sys.stderr, u'error: unrecognized mode, please use mode a or s'
    return 1


if __name__ == '__main__':
    sys.exit(main(len(sys.argv), sys.argv))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
