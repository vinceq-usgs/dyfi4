#! /usr/bin/env python3

"""
screenshot
==========

Command line tool to create a .png static image from DYFI
aggregated GeoJSON data

"""

import argparse
import json
from geojson import Feature,Point

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
        '--configfile',action='store',default='./config.yml',
        help='Specify config file'
    )

    if not args:
      args=parser.parse_args()

    evid=args.evid

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

    infile='data/'+evid+'/dyfi_geo_10km.geojson'
    with open('leaflet/data.js','w') as f:
      f.write('var eventEpicenter=')
      f.write(json.dumps(eventGeoJSON))
      f.write('\n\n')
      f.write('var data10km=')

      with open(infile,'r') as inf:
        f.write(inf.read())
      
"""
#cp ../data/$1/dyfi_geo_10km.geojson tmp.geojson
#echo 'data=' > data.js
#cat tmp.geojson >> data.js

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --disable-gpu --screenshot file:///Users/Vinceq/repos/dyfi4/leaflet/viewer.html

#rm tmp.geojson
"""


if __name__=='__main__':
  main()

