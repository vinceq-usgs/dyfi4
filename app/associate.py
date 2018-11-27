#! /usr/bin/env python3

"""
rundyfi.py
==========

"""

import sys
import os
import argparse

parser=argparse.ArgumentParser(
    prog='app/associate.py',
    description='Associate entries to this event'
)    
parser.add_argument(
    'evid',type=str,
    help='Event ID'
)
parser.add_argument(
    '--time',action='store',default=0.5,
    help='forward time window (hrs)'
)
parser.add_argument(
    '--dist',action='store',default=100,
    help='distance threshold (km)'
)
parser.add_argument(
    '--minint',action='store',default=None,
    help='minimum intensity'
)
parser.add_argument(
    '--maxint',action='store',default=None,
    help='maximum intensity'
)
exgroup=parser.add_mutually_exclusive_group()
exgroup.add_argument(
    '--from',action='store_true',default=False,
    help='search particular event (also try "unknown")'
)
exgroup.add_argument(
    '--fromall',action='store_true',default=False,
    help='search all events including larger ones'
)
parser.add_argument(
    '--checkold',action='store_true',default=False,
    help='search events older than 7 days (ignored by --from/--fromall)'
)
parser.add_argument(
    '--replace',action='store',default=False,
    help='Make changes (default is view only)'
)
parser.add_argument(
    '--configfile',action='store',default='./config.yml',
    help='Specify config file'
)


def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Associator,Lock

    evid=args.evid
    Lock('associate.'+evid,silent=True)
         
        
    directives={}
    directiveOptions=('evid','time','dist','minint','maxint',
                      'from','fromall','checkold')
    for key,val in vars(args).items():
        if val and key in directiveOptions:
            directives[key]=val
    print('Directives:',directives)
    
    associator=Associator(evid,directives,configfile=args.configfile)

    if associator.replacements and args.replace:
        associator.replace()

    print('Done with',evid)
    return evid


if __name__=='__main__':
    args=parser.parse_args()
    main(args)




