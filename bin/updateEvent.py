#! /usr/bin/env python

"""
updateEvent.py
============

This will update or create an event from ComCat or a file

"""

import os
import sys
import json
import argparse

# Global database handler
DB=None

parser=argparse.ArgumentParser(
    prog='app/updateEvent.py',
    description='Read event data from USGS ComCat'
)
parser.add_argument(
    'evid',type=str,
    help='Event ID'
)
parser.add_argument(
    '--file',action='store',
    help='Read from JSON file instead of feed (implies --noexternal)'
)
parser.add_argument(
    '--raw',action='store_true',default=False,
    help='Print raw feed and exit'
)
parser.add_argument(
    '--noexternal',action='store_true',default=False,
    help='Do not look for external update'
)
parser.add_argument(
    '--norun',action='store_true',default=False,
    help='Do not run rundyfi.py'
)
parser.add_argument(
    '--trigger',action='store_true',default=False,
    help='Trigger this event'
)
parser.add_argument(
    '--configfile',action='store',default='./config.yml',
    help='Specify config file'
)

def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Run

    evid=args.evid

    run=Run(configfile='./bin/localconfig.yml')

    if args.raw:
        print('Getting raw comcat data only.')
        evid=run.update(evid,raw=True)
        exit()

    if args.file:
        print('Reading from file',args.file)
        with open(args.file,'r') as f:
            triggerjson=json.load(f)
        evid=run.update(evid,inputJson=triggerjson)
        # This will populate run.duplicates if necessary

    if not args.noexternal and not args.file:
        # Call comcat
        # This will populate run.duplicates if necessary
        run.update(evid)

    if (run.event=='DELETED'):
        print('Got deleted eventid',evid)

    if args.trigger:
        run.runEvent(evid,update=False,findDuplicates=True,norun=args.norun)
    else:
        print('Stopping, use --trigger to continue.')
        exit()

    print('Done with updateEvent.py.')
    exit()

if __name__=='__main__':
    args=parser.parse_args()
    main(args)


