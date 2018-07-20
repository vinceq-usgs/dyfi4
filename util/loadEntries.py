#! /usr/bin/env python
"""

Usage: util/loadEntries.py --check --config [configfile]

Looks for raw entry files in data/incoming
Mostly stub to dyfi/incoming.py?
Note: Run from getEntries.py

Process loop:

For each response:
  Write to extended table
  If event doesn't exist in table:
    Save stub in event table (invisible=1)
    Run getEvent.py (separate process)


"""

import sys
import argparse
import os
import os.path

parser=argparse.ArgumentParser(
    prog='util/loadEntries.py',
    description='Download incoming responses and save to extended table'
)
parser.add_argument(
    '--check',action='store_true',
    help='Count files in directory but do not process them'
)
parser.add_argument(
    '--maxfiles',action='store',type=int,
    help='Limit the number of files to process'
)
parser.add_argument(
    '--configfile',action='store',default='./util/localconfig.yml',
    help='Specify config file'
)


def main(args):
    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Lock,Config
    
    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'.')))
    from modules.incoming import Incoming

    if not args.check:
        Lock('loadEntries')

    config=Config(args.configfile)
    incoming=Incoming(config)
    pendingFiles=incoming.checkIncoming()
    nfiles=len(pendingFiles)
    print('loadEntries.py: Got %s responses in %s' % (nfiles,config.directories['incoming']))

    if args.check:
        exit()

    count=0
    for file in pendingFiles:
        if args.maxfiles and count>=args.maxfiles:
            print('Processed',count,'files, stopping.')
            break

        if 'healthcheck' in file:
            os.remove(file)
            continue

        count+=1
        print('Processing',file)
        # This will save file and increment newresponses
        # This will also check the eventid in the Event table.
        # If the event has a different goodid, this will change the
        # entry ID accordingly
        entry=incoming.saveFile(file)

        if not entry:
            print('Ignoring file',file)
            incoming.remove(file,bad=True)
            continue

        print('Saved to subid %s, deleting' % entry.subid)
        incoming.remove(file)
        continue

    # Continue processing here
    return count


if __name__=='__main__':
    args=parser.parse_args()
    main(args)

