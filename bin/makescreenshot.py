#! /usr/bin/env python3

"""
screenshot.py
=============

Command line tool to create a .png static image from DYFI
aggregated GeoJSON data.

Usage: leaflet/screenshot.py eventid [dyfi_geo_10km.jpg]

This creates the file 
- leaflet/screenshot.png 
and saves a copy to
- data/eventid/dyfi_geo_10km.jpg

"""

import argparse
import json
from geojson import Feature,Point
import subprocess
import os
import shutil

from context import dyfi
from dyfi import Db,Config,Event

def main(args=None):

    parser=argparse.ArgumentParser(
        description='Create static image .png files for a given event'
    )
    parser.add_argument(
        'evid',type=str,
        help='Event ID'
    )
    parser.add_argument(
        'file',type=str,nargs='?',default='dyfi_geo_10km.geojson',
        help='GeoJSON input file'
    )
    parser.add_argument(
        '--configfile',action='store',default='./config.yml',
        help='Specify config file'
    )

    if not args:
      args=parser.parse_args()

    evid=args.evid
    inputfile=args.file

    config=Config(args.configfile)
    db=Db(config)
    event=Event(db.loadEvent(evid))
    if not event:
        raise NameError('No data for event '+evid)

    # Create event GeoJSON

    geometry=Point((event.lon,event.lat))
    props=event.toGeoJSON().properties
 
    eventGeoJSON = Feature(geometry=geometry)
    for key,val in event.toGeoJSON().properties.items():  
      eventGeoJSON['properties'][key]=val 

    # Copy geocoded GeoJSON

    # Create data.js file and run Chrome

    # Save output

    infile='data/'+evid+'/'+inputfile
    with open('leaflet/data.js','w') as f:
      f.write('var eventEpicenter=')
      f.write(json.dumps(eventGeoJSON))
      f.write('\n\n')
      f.write('var data10km=')

      with open(infile,'r') as inf:
        f.write(inf.read())
      
      command=['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
'--headless',
'--disable-gpu', 
'--screenshot',
'file:///Users/Vinceq/repos/dyfi4/leaflet/viewer.html']

      tmpfile='screenshot.png'
      if os.path.isfile(tmpfile):
        os.unlink(tmpfile)

      subprocess.call(command)
      if not os.path.isfile(tmpfile):
        print('ERROR: Could not create',tmpfile)
        exit()

      pngfile='data/'+evid+'/'+inputfile.replace('geojson','png')
      shutil.copyfile(tmpfile,pngfile)
      print('Created file',pngfile)



if __name__=='__main__':
  main()

