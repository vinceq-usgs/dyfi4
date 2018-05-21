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
    description='Create DYFI products. An event ID is required. See the :obj:`Product Guide` for an explanation of the output products.'
)
parser.add_argument(
    'evid',type=str,
    help='Event ID (required)'
)
parser.add_argument(
    '--push',action='store_true',
    help='Push event products to PDL (not yet implemented)'
)
parser.add_argument(
    '--redo',action='store_true',
    help='Redo all products even if they exist'
)
parser.add_argument(
    '--configfile',action='store',default='./config.yml',
    help='Specify config file'
)
parser.add_argument(
    '--debug',action='store_true',default=None,
    help='Special debug mode'
)


def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import DyfiContainer,Contents

    print('--------------------')
    print('Starting dyfi.py: ',time.asctime(time.localtime()))

    evid=args.evid

    # TODO: Add directives like --create, --redo, --push
    container=DyfiContainer(evid)
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
