#! /usr/bin/env python

"""

getEntries.py
=============

"""

import os
import sys
import argparse
import subprocess

parser=argparse.ArgumentParser(
    prog='app/getEntries.py',
    description='Download response files from outside servers'
)
parser.add_argument(
    '--check',action='store_true',
    help='Check servers instead of processing'
)
parser.add_argument(
    '--nodelete',action='store_true',default=False,
    help='Keep remote responses (for testing only)'
)
parser.add_argument(
    '--config',action='store',default='bin/config.yml',
    help='Specify config file'
)


def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Lock,Config

    Lock('getEntries')

    config=Config(args.config)
    resp=config.responses
    incomingDir=config.directories['incoming']

    if not os.path.isdir(incomingDir):
        os.makedirs(incomingDir,exist_ok=True)

    # This architecture is specific to the USGS Earthquake Pages server.

    for remote in resp['servers']:
        remoteServer=remote['server']
        remoteDir=remote['dir']

        if args.check:
            remoteCommand=resp['remoteCheck'].format(
                server=remoteServer,
                dir=remoteDir)

            command=remoteCommand.split()
            proc=subprocess.Popen(command,stdout=subprocess.PIPE)
            results=proc.stdout.read()

            # Remove one for 'total' line
            num=len(results.splitlines())-1
            print(remoteServer,'has',num,'responses.')

        else:
            remove='' if args.nodelete else '--remove-sent-files'
            remoteCommand=resp['remoteGet'].format(
                remove=remove,
                server=remoteServer,
                dir=remoteDir,
                destination=incomingDir)

            print(remoteCommand)
            command=remoteCommand.split()
            proc=subprocess.Popen(command,stdout=subprocess.PIPE)
            results=proc.stdout.read()


if __name__=='__main__':
    args=parser.parse_args()
    if 0:
        print('DEBUG')
        args.nodelete=True
        args.check=True

    main(args)

