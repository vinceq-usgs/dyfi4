#! /usr/bin/env python3

"""
makescreenshot.py
=============

Command line tool to create a .png static image from DYFI
aggregated GeoJSON data.

Usage: 
bin/makescreenshot.py GeoJSON file --output file.png
This attempts to create an image file from a GeoJSON file.

"""

import argparse
import json
from geojson import Feature,Point
import subprocess
import os
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dyfi import Db,Event,staticMap

def main(args=None):

    parser=argparse.ArgumentParser(
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

    if not args:
      args=parser.parse_args()

    inputfile=args.input
    outputfile=args.output
    print('Creating image file from GeoJSON file',inputfile,'to',outputfile)

    if staticMap.createFromGeoJSON(inputfile,outputfile=outputfile,
      config=args.configfile):

      print('Success, created',outputfile)

    else:
        print('ERROR: Could not create',outputfile)

    exit()

if __name__=='__main__':
  main()

