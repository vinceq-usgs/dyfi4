#! /usr/bin/env python3

"""
makescreenshot.py
=============

Command line tool to create a .png static image from DYFI
aggregated GeoJSON data.

Usage:
app/makescreenshot.py [GeoJSON file]
This attempts to create an image file from a GeoJSON file.

"""

import argparse
import os
import sys


parser=argparse.ArgumentParser(
    prog='app/makescreenshot.py',
    description='Create a static image .png file for a given event. The DYFI output must already exist; (run :obj:`rundyfi.py` first). The output is a PNG file (default `./screenshot.png`).'
)
parser.add_argument(
    'input',type=str,
    help='GeoJSON file'
)
parser.add_argument(
    'output',type=str,nargs='?',default='screenshot.png',
    help='output filename'
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
