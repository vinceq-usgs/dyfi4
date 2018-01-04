#! /usr/bin/env python
"""

Usage: app/incoming.py --check --config [configfile]

Mostly a stub to dyfi/responses.py
Note: Run from cron

Process loop:

Download responses
For each response:
  Write to extended table
  If event doesn't exist in table:
    Save stub in event table (invisible=1)
    Run getEvent.py (separate process)
    

"""

import sys
import argparse
import os.path
import time

PENDING_FILES_MAX=50 # Don't download more responses if more than this

parser=argparse.ArgumentParser(
    prog='app/incoming.py',
    description='Download incoming responses and save to extended table'
)
parser.add_argument(
    '--check',action='store_true',
    help='Check for pending responses but don\'t download them'
)
parser.add_argument(
    '--noremote',action='store_true',
    help='Don\'t access remote servers'
)
parser.add_argument(
    '--nodelete',action='store_true',default=False,
    help='Don\'t remove remote files (for debugging only)'
)
parser.add_argument(
    '--configfile',action='store',default='./config.yml',
    help='Specify config file'
)


def main(args):
    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Lock
    from dyfi import Responses

    if not args.check:
        Lock('incoming')

    resp=Responses(args.configfile)
    pendingFiles=resp.checkIncomingDir()

    if args.check:
        nfiles=len(pendingFiles)
        print('incoming.py: Got',nfiles,'responses in incoming')
        if not args.noremote:
            resp.downloadServers(checkonly=True)
        exit()

    while(1):
        if not args.noremote and len(pendingFiles)<=PENDING_FILES_MAX:
            resp.downloadServers(nodelete=args.nodelete)
            time.sleep(1)
            pendingFiles=resp.checkIncomingDir()

        if len(pendingFiles)==0:
            print('No responses found, exiting.')
            exit()

        for file in pendingFiles:
            print('Processing',file)
            entry=resp.processFile(file)

            if entry:
                subid=entry.subid
                print('Saved this file to subid',subid,'now deleting')
                os.remove(file)
                continue

            print('Ignoring file',file)
            if not resp.removeFile(file):
                print('WARNING: Could not remove',file)
                continue

        pendingFiles=[]


if __name__=='__main__':
    args=parser.parse_args()
    main(args)



