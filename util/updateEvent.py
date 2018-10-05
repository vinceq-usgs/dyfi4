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
    '--configfile',action='store',default='util/localconfig.yml',
    help='Specify config file'
)

def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Config

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'.')))
    from modules.run import Run

    evid=args.evid

    run=Run(Config(args.configfile))

    if args.raw:
        print('Getting raw comcat data only.')
        rawdata=run.loadComcat(evid,raw=True)
        print(rawdata)
        exit()

    if args.file:
        print('Updating %s with %s.' % (evid,args.file))
        with open(args.file,'r') as f:
            rawInput=f.read()
        # This will populate run.duplicates if necessary
        run.loadComcat(evid,rawInput=rawInput)
        newid=run.updateEvent()

    if not args.noexternal and not args.file:
        print('Updating %s from Comcat.' % evid)
        # This will populate run.duplicates if necessary
        run.loadComcat(evid)
        newid=run.updateEvent()

    if (run.event=='DELETED'):
        print('Got deleted eventid',evid)

    if args.trigger:
        if not newid:
            print('WARNING: Could not get data, loading current Event data.')
            newid=evid
        run.runEvent(evid=newid,findDuplicates=True,norun=args.norun)
    else:
        print('Stopping, use --trigger to continue.')

    print('Done with updateEvent.py.')
    exit()

if __name__=='__main__':
    args=parser.parse_args()
    main(args)


