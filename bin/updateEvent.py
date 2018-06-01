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
import urllib.request
import subprocess

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
    help='Read from file instead of feed (implies --noupdate)'
)
parser.add_argument(
    '--raw',action='store_true',default=False,
    help='Print raw feed and exit'
)
parser.add_argument(
    '--noupdate',action='store_true',default=False,
    help='Do not do external update'
)
parser.add_argument(
    '--check',action='store_true',default=False,
    help='Check update but don\'t write or process'
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
    from dyfi import Config,Event,Db,Run

    update=False if args.noupdate else True
    evid=args.evid

    run=Run(configfile='./bin/localconfig.yml')

    if args.check:
        evid=run.update(evid,check=True)
        exit()

    if args.file:
        with open(args.file,'r') as f:
            triggerjson=json.load(f)
        evid=run.update(evid,raw=triggerjson)
        update=False

    run.runEvent(evid,update=update,findDuplicates=True)
    exit()

if __name__=='__main__':
    args=parser.parse_args()
    main(args)


