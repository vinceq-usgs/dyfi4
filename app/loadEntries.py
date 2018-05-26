#! /usr/bin/env python
"""

Usage: app/loadEntries.py --check --config [configfile]

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
import time

parser=argparse.ArgumentParser(
    prog='app/loadEntries.py',
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
    '--configfile',action='store',default='./config.yml',
    help='Specify config file'
)


def main(args):
    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Lock,Incoming,Config

    if not args.check:
        Lock('incoming')

    incoming=Incoming(Config(args.configfile))
    pendingFiles=incoming.checkIncoming()
    nfiles=len(pendingFiles)
    print('loadEntries.py: Got',nfiles,'responses in incoming')

    if args.check:
        exit()

    count=0
    for file in pendingFiles:
        if args.maxfiles and count>=args.maxfiles:
            print('Processed',count,'files, stopping.')
            exit()

        if 'healthcheck' in file:
            os.remove(file)
            continue

        count+=1 
        print('Processing',file)
        # This will save file and increment newresponses
        entry=incoming.processFile(file)

        if not entry:
            print('Ignoring file',file)
            incoming.remove(file,bad=True)
            continue

        subid=entry.subid
        print('Saved this file to subid '+subid+', now deleting')
        incoming.remove(file)
        continue


if __name__=='__main__':
    args=parser.parse_args()
    main(args)

