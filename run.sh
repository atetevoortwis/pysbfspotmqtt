#!/bin/sh
cd "$(dirname "$0")"
. ./venv/bin/activate
python3 logsma.py 2>&1 | logger -s
