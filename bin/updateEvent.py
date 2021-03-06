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
    '--configfile',action='store',default='./config.yml',
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
    if not event:
        print('No data found.')
        exit()

    if event.eventid!=evid:
        print('Event ID changed from %s to %s' % (evid,event.eventid))
        evid=event.eventid

    print('Event data:')
    print(event)

    if args.save:
        print('Saving to event table.')
        db=Db(Config(args.configfile))
        # TODO: Don't clobber newresponses
        saved=db.save(event)

        if saved:
            print('Saved',saved,'in database.')
        else:
            print('Warning: problem saving this event.')

        print('Dups:',event.duplicates)
        if event.duplicates:
            db.saveDuplicates(evid,event.duplicates)

    print('Done with',evid)


if __name__=='__main__':
    args=parser.parse_args()
    main(args)


