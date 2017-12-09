#! /usr/bin/env python

"""
readEvent.py
============

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
    '--raw',action='store_true',
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
    from dyfi import Config,ComcatEvent,Event

    evid=args.evid

    event=ComcatEvent(evid)
    contents=event.contents

    if args.raw:
        print(json.dumps(contents,indent=2))
        exit()

    event=Event.createFromContents(contents)
    if event.eventid!=evid:
        print('Event ID changed from %s to %s' % (evid,event.eventid))
        evid=event.eventid

    if args.save:
        print('Saving to event table.')
        event.save(config=Config(args.config))


if __name__=='__main__':
    args=parser.parse_args()
    main(args)


