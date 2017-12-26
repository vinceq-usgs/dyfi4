#! /usr/bin/env python

"""

getEntries.py
=============

"""

import os
import sys
import argparse

parser=argparse.ArgumentParser(
    prog='app/getEntries.py',
    description='Download response files from outside servers'
)
parser.add_argument(
    '--check',action='store_true',
    help='Check servers instead of processing'
)
parser.add_argument(
    '--nodelete',action='store_true',default=True,
    help='Keep remote responses (for testing only)'
)
parser.add_argument(
    '--config',action='store',default='./config.yml',
    help='Specify config file'
)

def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Lock,Config,Db

    config=Config(args.config)
    incomingDir=config.directories['incoming']

    Lock('getEntries')

    if not os.path.isdir(incomingDir):
        os.makedirs(incomingDir,exist_ok=True)

    if args.check:
        exit()

    template=config.responses['serverTemplate']
    remotes=config.responses['remotes']
    print('Got remotes:',remotes)
    for remote in remotes.split(','):
        remoteServer=template.format(server=remote)
        print('Checking remote',remoteServer)
    

if __name__=='__main__':
    args=parser.parse_args()
    main(args)

