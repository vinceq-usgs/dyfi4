#! /usr/bin/env python3

"""
dyfi
====

Command line tool to create products for a given event.
This will also run the 'push' tool to send products to PDL
if the '-push' flag is used.

"""
import time
import argparse
import os
import sys

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from dyfi import DyfiContainer

def main(args=None):

    print('--------------------')
    print('Starting dyfi.py: ',time.asctime(time.localtime()))

    # Handle arguments
    parser=argparse.ArgumentParser(
        description='Create DYFI products for a given event ID'
    )
    parser.add_argument(
        'evid',type=str,
        help='Event ID'
    )
    parser.add_argument(
        '--push',action='store_true',
        help='Push event products to PDL'
    )
    parser.add_argument(
        '--redo',action='store_true',
        help='Redo all products even if they exist'
    )
    parser.add_argument(
        '--configfile',action='store',default='./config.yml',
        help='Specify config file'
    )

    if not args:
      args=parser.parse_args()
    print(repr(args))

    evid=args.evid

    # Load event
    # TODO: Add directives like --create, --redo, --push
    container=DyfiContainer(evid)

    if not container:
        raise NameError('No data for event '+evid)

    print('Done with',evid)
    return container


if __name__=='__main__':
    main()
