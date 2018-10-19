#! /usr/bin/env python
"""

Usage: bin/push.py evid [--delete]

1. Create event_data.xml
2. Find parameters for push command
3. Send push command

"""

import sys
import argparse
import shutil
import os.path
import yaml
import json
import subprocess
import defusedxml.minidom as dom


parser=argparse.ArgumentParser(
    prog='bin/push.py',
    description='Push via PDL'
)
parser.add_argument(
    'evid',action='store',
    help='Event ID'
)
parser.add_argument(
    '--noaux',action='store_true',default=False,
    help='Skip the creation of auxilliary files for Event Pages'
)
parser.add_argument(
    '--delete',action='store_true',default=False,
    help='Send a Delete signal for this event'
)
parser.add_argument(
    '--trigger',action='store_true',default=False,
    help='Activate PDL'
)
parser.add_argument(
    '--configfile',action='store',default='bin/localconfig.yml',
    help='Specify config file'
)


def callPdl(params,datadir,config,delete=False,trigger=False):

    e=params.getElementsByTagName('event_data')[0]
    ee=e.getElementsByTagName('event')[0]
    c=e.getElementsByTagName('cdi_summary')[0]

    network=e.getAttribute('network')
    code=network+e.getAttribute('eventid')
    
    flags={
        '--send':None,
        '--source':'us',
        '--type':'dyfi',
        '--code':code,
        '--eventsource':network,
        '--eventsourcecode':code[2:]
    }

    if args.delete:
        flags['--delete']=None;

    else:
        for p in ('latitude','longitude','depth','magnitude'):
            flags['--'+p]=ee.getAttribute(p)

        eventtime=(ee.getAttribute('event_timestamp')+'Z').replace(' ','T')
        flags['--eventtime']=eventtime

        processtime=(e.getAttribute('process_timestamp')+'Z').replace(' ','T')
        flags['--updateTime']=processtime
        flags['--directory']=datadir
        flags['--property-num-responses']=c.getAttribute('nresponses') or 0
        flags['--property-maxmmi']=c.getAttribute('max_intensity') or 0

    commandList=config['pushcommand'].split(' ')
    for k,v in flags.items():
        flag=k if v is None else '%s=%s' % (k,v)
        commandList.append(flag)

    commandList=(' '.join(commandList)).split(' ')
    if not trigger:
        print(' '.join(commandList))
        print('Use --trigger flag to send to PDL')
        return

    result=subprocess.call(commandList,stderr=subprocess.STDOUT,timeout=60)


def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Config,Event

    evid=args.evid

    config=Config(args.configfile)
    datadir='%s/%s' % (config.directories['data'],evid)
    conf=config.push

    print("Pushing",evid)

    if not args.noaux and 'auxcommand' in config.aux:
        commandList=config.aux['auxcommand'].split(' ')+[evid]
        result=subprocess.call(commandList,stderr=subprocess.STDOUT)

    datafile='%s/%s' % (datadir,conf['datafile'])
    params=dom.parse(datafile)
    callPdl(params,datadir,conf,delete=args.delete,trigger=args.trigger)


if __name__=='__main__':
    args=parser.parse_args()
    main(args)

