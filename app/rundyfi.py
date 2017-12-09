#! /usr/bin/env python3

"""
rundyfi.py
==========

"""

import time
import argparse
import os
import sys

parser=argparse.ArgumentParser(
    prog='app/rundyfi.py',
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

def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import DyfiContainer,Contents

    print('--------------------')
    print('Starting dyfi.py: ',time.asctime(time.localtime()))
    print(repr(args))

    evid=args.evid

    # Load event
    # TODO: Add directives like --create, --redo, --push
    container=DyfiContainer(evid)

    if not container:
        raise NameError('No data for event '+evid)

    Contents(container).toXML(save=True)

    # TODO: Push should be a separate object
    #if args.push:
    #  Push.push(contents)
    #  container.resetResponsesCount()

    print('Done with',evid)
    return container


if __name__=='__main__':
    args=parser.parse_args()
    main(args)
