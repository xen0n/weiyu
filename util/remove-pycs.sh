#!/bin/bash

UTIL_DIR="$( cd "$( dirname ${BASH_SOURCE[0]} )" && pwd )"

cd "${UTIL_DIR}/.."

for subdir in weiyu kbslib; do
    find "${subdir}" -name '*.pyc' -type f | xargs rm
done


# vim:ai:et:ts=4:sw=4:sts=4:fenc=utf8:
