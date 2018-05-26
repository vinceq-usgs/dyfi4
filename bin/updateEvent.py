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
    prog='app/readEvent.py',
    description='Read event data from USGS ComCat'
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
    '--check',action='store_true',default=False,
    help='Check only but no database write'
)
parser.add_argument(
    '--trigger',action='store_true',default=False,
    help='Trigger this event'
)
parser.add_argument(
    '--configfile',action='store',default='./config.yml',
    help='Specify config file'
)

class Comcat:

    SERVER = 'earthquake' #comcat server name
    URLBASE = 'https://[SERVER].usgs.gov/fdsnws/event/1/query?'.replace('[SERVER]',SERVER)
    ALLPRODURL = 'https://earthquake.usgs.gov/fdsnws/event/1/query?'
    TIMEOUT = 30;

    def __init__(self,query):

        url=self.URLBASE+query+'&format=geojson'
        print('Requesting:',url)

        try:
            contents=urllib.request.urlopen(url,timeout=self.TIMEOUT).read().decode('utf8')

        except urllib.error.URLError:
            contents=None

        self.contents=contents


class ComcatEvent:

    QUERY='format=geojson&includesuperseded=[SUPERCEDED]&eventid=[EVENTID]'

    def __init__(self,evid,includeSuperseded=False):
        query=self.QUERY.replace('[EVENTID]',evid)
        superseded='true' if includeSuperseded else 'false'
        query=query.replace('[SUPERCEDED]',superseded)

        contents=Comcat(query).contents
        if contents:
            try:
                contents=json.loads(contents)
            except json.JSONDecodeError as e:
                print('Possible malformed contents: '+e.msg)
                return

        self.contents=contents

#####
#
# Functions to handle duplicates
#
#####

def createStubEvent(data):
    global DB

    if 'eventid' not in data:
        raise ValueError('Cannot create event without evid')

    print('Db: Creating stub event for',data['eventid'])
    results=DB.rawdb.save('event',data)
    return results


def handleDuplicates(goodid,dups):
    global DB

    for dupid in dups:
        dupevent=Event(dupid,missing_ok=True)

        # If the dup event doesn't yet exist, create a stub
        # to warn future entries where to go

        if not dupevent:
            DB.createStubEvent(dupid,{'good_id':goodid})
            continue

        if 'good_id' in dupevent and dupevent['good_id']!=goodid:
            print('Db: Updating goodid for',dupid)
            DB.rawdb.updateRow('event',dupid,'good_id',goodid)


        nMoved=0

        print('TODO: Still need to grab newresponses from',dupid)
        # entriesToMove=<all entries with eventid=dupid>
        # foreach entry in entriesToMove: 
        #     DB.rawdb.updateRow(table,subid,'eventid',goodid
        #     movedentries++
        
        if nMoved: 
            print('Moved %i entries from %s to %s' % (nMoved,dupid,goodid))
            DB.addNewresponse(goodid,movedentries)

        continue


def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Config,Event,Db
    global DB

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

    if not contents:
        print('No data found.')
        exit()

    event=Event.createFromContents(contents)
    if not event:
        print('Could not read raw contents.')
        exit()

    if event.eventid!=evid:
        print('WARNING! WARNING! WARNING!')
        print('Event ID changed from %s to %s' % (evid,event.eventid))
        print('WARNING! WARNING! WARNING!')
        evid=event.eventid

    print('Event data:',event)
    if event.duplicates:
        print('Duplicates:',event.duplicates)

    if args.check:
        print('Stopping.')
        exit()

    print('Saving to event table.')
    DB=Db(Config(args.configfile))
    # TODO: Don't clobber newresponses
    saved=DB.save(event)

    if saved:
        print('Saved',saved,'in database.')
    else:
        print('Warning: problem saving this event, stopping.')
        exit()

    if event.duplicates:
        handleDuplicates(evid,event.duplicates)

    if not args.trigger:
        print('Not running event.')
        exit()

    print('Running event.')
    subprocess.run(['app/rundyfi.py',evid])

    print('Done with',evid)
    exit()

if __name__=='__main__':
    args=parser.parse_args()
    main(args)


