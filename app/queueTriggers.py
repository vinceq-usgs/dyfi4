#! /usr/bin/env python
"""

run from cron

Usage: app/queueTriggers.py --check --config [configfile]

This program runs through the event table and finds events to run.
A stub to Pending.py

"""

import sys
import argparse
import os.path

parser=argparse.ArgumentParser(
    prog='app/queueTriggers.py',
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
    pending=Pending(maxruns=0,configfile=args.configfile)

    if args.check:
        pending.countEvents()
        pending.displayEvents()
        exit()

    pending.loop()


if __name__=='__main__':
    args=parser.parse_args()
    main(args)



