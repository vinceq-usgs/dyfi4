#! /usr/bin/env python3

"""
makescreenshot.py
=============

Command line tool to create a .png static image from DYFI
aggregated GeoJSON data.

Usage:
app/makescreenshot.py GeoJSON file --output file.png
This attempts to create an image file from a GeoJSON file.

"""

import argparse
import os
import sys


parser=argparse.ArgumentParser(
    prog='app/makescreenshot.py',
    description='Create static image .png files for a given event'
)
parser.add_argument(
    'input',type=str,
    help='GeoJSON file'
)
parser.add_argument(
    'output',type=str,nargs='?',default='screenshot.png',
    help='output (default is screenshot.png)'
)
parser.add_argument(
    '--configfile',action='store',default='./config.yml',
    help='Specify config file'
)


def main(args):

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from dyfi import Config,Map

    inputfile=args.input
    outputfile=args.output

    if Map.GeoJSONtoImage(inputfile,outputfile,Config(args.configfile)):
      print('Success, created',outputfile)

    else:
        print('ERROR: Could not create',outputfile)

    exit()

if __name__=='__main__':
    args=parser.parse_args()
    main(args)
