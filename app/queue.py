#! /usr/bin/env python
"""

run from cron
use flock to ensure that multiple processes never run concurrently

Usage: app/queue.py --check --config [configfile]

Process loop:

Get list of events with nresponses>n
  Sort by nresponses
  For each event: run event

"""

import sys
import argparse
import os.path
import time

parser=argparse.ArgumentParser(
    prog='app/queue.py',
    description='Check for events with pending responses and run them'
)
parser.add_argument(
    '--check',action='store_true',default=False,
    help='Check for pending events but don\'t run them'
)
parser.add_argument(
    '--maxruns',action='store',type=int,default=5,
    help='Maximum number of event runs before exiting'
)
parser.add_argument(
    '--configfile',action='store',default='./config.yml',
    help='Specify config file'
)


def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Lock
    from dyfi import Pending

    if not args.check:
        Lock('queue')

    print(vars(args))
    pending=Pending(**vars(args))


if __name__=='__main__':
    args=parser.parse_args()
    main(args)



