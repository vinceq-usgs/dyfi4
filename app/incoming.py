#! /usr/bin/env python
"""

run from cron
use flock to ensure that multiple processes never run concurrently

Usage: app/incoming.py --check --config [configfile]

Process loop:

Download responses
For each response:
  Write to extended table
  If event doesn't exist in table:
    Save stub in event table (invisible=1)
    Run getEvent.py (separate process)
    

"""

import sys
import argparse
import os.path
import time

parser=argparse.ArgumentParser(
    prog='app/incoming.py',
    description='Download incoming responses and save to extended table'
)
parser.add_argument(
    '--check',action='store_true',
    help='Check for pending responses but don\'t download them'
)
parser.add_argument(
    '--nofeed',action='store_true',default=False,
    help='Don\'t check the USGS Event Feed for event data'
)
parser.add_argument(
    '--configfile',action='store',default='./config.yml',
    help='Specify config file'
)


def main(args):
    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Lock
    from dyfi import Responses

    if not args.check:
        Lock('incoming')

    responses=Responses(**vars(args))


if __name__=='__main__':
    args=parser.parse_args()
    main(args)



