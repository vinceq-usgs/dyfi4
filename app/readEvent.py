#! /usr/bin/env python

"""
readEvent.py
============

# TODO: Find duplicates

"""

import os
import sys
import json
import argparse

parser=argparse.ArgumentParser(
    prog='app/readEvent.py',
    description='Read event data from USGS'
)
parser.add_argument(
    'evid',type=str,
    help='Event ID'
)
parser.add_argument(
    '--file',action='store',
    help='Read from file instead of feed'
)
parser.add_argument(
    '--raw',action='store_true',default=False,
    help='Print raw feed and exit'
)
parser.add_argument(
    '--save',action='store_true',
    help='Save to database'
)
parser.add_argument(
    '--config',action='store',default='./config.yml',
    help='Specify config file'
)


def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Config,ComcatEvent,Event,Db

    evid=args.evid

    if args.file:
        with open(args.file,'r') as f:
            contents=json.load(f)

    else:
        event=ComcatEvent(evid)
        contents=event.contents

    if args.raw:
        print(json.dumps(contents,indent=2))
        exit()

    event=Event.createFromContents(contents)
    if event.eventid!=evid:
        print('Event ID changed from %s to %s' % (evid,event.eventid))
        evid=event.eventid

    print('Event data:')
    print(event)

    if args.save:
        print('Saving to event table.')
        db=Db(Config(args.config))
        if not db.save(event):
            print('Warning: problem with saving this event.')

    print('Done with',evid)


if __name__=='__main__':
    args=parser.parse_args()
    main(args)


