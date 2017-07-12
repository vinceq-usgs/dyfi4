#! /usr/local/bin/python3

import argparse
from urllib import request
import json


class Geoserve():
    """
A module to access the USGS Geoserve Places Service, 
earthquake.usgs.gov/ws/geoserve.

Usage:
    From the command line, geoserve.py lat lon [gettype]
    Or call from module:
        from geoserve import Geoserve
        geo=Geoserve(lat,lon)

        print(geo) : returns string version of preferred name
        geo.availabletypes : list of datatypes with data (see below)
        geo.getname : returns string version of preferred name
        geo.lat,geo.lon : store input lat/lon
        geo.names : list of raw output by datatype
        geo.preferredtype: type used for preferred name
        geo.raw : stores raw output from server
        geo.url : stores URL for Geoserve (including parameters)

    """

    RAWURL='http://earthquake.usgs.gov' \
        + '/ws/geoserve/regions.json?latitude={}&longitude={}'

    """

GOODPRODUCTTYPES is a list of acceptable producttypes that can be 
used to build a stringified location name. The module will 
iterate through the typenames in order until it finds one with 
an existing proplist, and concatenates those values.  

"""
    GOODPRODUCTTYPES=[
        {
            'typename':'admin',
            'proplist':['region','country']
        },
        {
            'typename':'fe',
            'proplist':['name']
        }
    ]

    def __init__(self,lat,lon):
        self.lat=lat
        self.lon=lon
        self.url=self.RAWURL.format(lat,lon)

        fh=request.urlopen(self.url)
        data=fh.read().decode('utf8')
        results=json.loads(data)
        if not results:
            print('WARNING: No results found (no connection?)')
            return
        fh.close
        self.raw=results

        if not self.raw:
            return

        typelist=[x['typename'] for x in self.GOODPRODUCTTYPES]
        self.names={}
        self.preferredtype=''
        self.availabletypes=[]

        for typename in typelist:
            if typename not in self.raw:
                continue
            features=self.raw[typename]['features']
            if not features:
                continue
            props=features[0]['properties']
            if not props:
                continue
            self.availabletypes.append(typename)
            self.names[typename]=props
            if not self.preferredtype:
                self.preferredtype=typename

    def getname(self):
        typename=self.preferredtype
        keylist=[x['proplist'] for x in self.GOODPRODUCTTYPES
                 if x['typename']==typename][0]
        proplist=self.names[typename]
        return(', '.join([proplist[x] for x in keylist]))

    def __str__(self):
        if hasattr(self,'name'):
            return(self.name)
        return(self.getname())

"""
"""

if __name__=='__main__':
    parser=argparse.ArgumentParser(
        description='Get a name for a lat/lon pair.')
    parser.add_argument('lat',type=float,
                        help='Latitude')
    parser.add_argument('lon',type=float,
                        help='Longitude')
    parser.add_argument('gettype',type=str,nargs='?',
                        help='Data type to query')

    args=parser.parse_args()

    geo=Geoserve(args.lat,args.lon)
    print(geo)

