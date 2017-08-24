#! /usr/bin/env python3

"""
makemovie.py
=============

Usage:

"""

import argparse
import json
from geojson import Feature,Point
import subprocess
import os
import shutil
import sys
import datetime
import copy
import apng

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dyfi import Db,Event,staticMap,Config,Entries,Product

class Movie:

    def __init__(self,args):

        self.dir='movie'
        self.framefiles=[]
        os.makedirs(self.dir,exist_ok=True)

        evid=args.evid
        inputfile='data/%s/dyfi_%s.geojson' % (evid,args.type)
        with open(inputfile,'r') as f:
            data=json.load(f)

        config=Config()
        event=Event(evid,config=config)
        entries=Entries(evid,config=config)
        totalcount=len(entries)
        print('Maximum',totalcount,'entries.')
        allentries=copy.deepcopy(entries.entries)

        eventtime=datetime.datetime.strptime(event.eventdatetime,'%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)

        t=0
        while (t+args.framelength)<=60*(args.tmax):
            t+=args.framelength

            inputfile='%s/tmp.%s.%i.geojson' % (self.dir,evid,t)
            outputfile='%s/tmp.%s.%i.png' % (self.dir,evid,t)
            if os.path.exists(outputfile):
                self.framefiles.append(outputfile)
                print(outputfile,'exists, skipping.')
                continue

            print('Making frame for t=%s s.' % t)

            # loop through partial datasets
            newentries=[]
            lasttime=eventtime+datetime.timedelta(seconds=t)

            for entry in allentries:
                entrytime=datetime.datetime.strptime(entry.time_now,'%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
                if entrytime<=lasttime:
                    newentries.append(entry) 

            newentries=Entries(evid,rawentries=newentries,config=config,load=False)
            nentries=len(newentries)
            print('This frame has',nentries,'entries.')
            aggregated=newentries.aggregate(args.type)

            if nentries>0:
                product=Product(dir=self.dir,data=aggregated,filename=inputfile,config=config,name=args.type)
                print('Made Product, now saving to',inputfile)
                print(product.create('geojson'))
                print('Created geojson.')

                outputfile=staticMap.createFromGeoJSON(inputfile,outputfile,config=config)
                product.filename=outputfile
                self.framefiles.append(outputfile)
                os.remove(inputfile)

        outputfile='movie/%s.apng' % evid
        self.filename=self.splice(outputfile)
        return 


    def partial_geosjon(self,args):
        pass


    def splice(self,outputfile):
        # Use up everything in self.dir
        # delete all tmp files

        files=self.framefiles
        apng.APNG.from_files(files,delay=500).save(outputfile)
        for file in files:
            os.remove(file)
        return outputfile


def main(args=None):

    parser=argparse.ArgumentParser(
        description='Create movie frames for a given event'
    )
    parser.add_argument(
        'evid',type=str,
        help='Event ID'
    )
    parser.add_argument(
        'tmax',type=int,nargs='?',default=60,
        help='Length of movie in minutes (default 60)'
    )
    parser.add_argument(
        'framelength',type=float,nargs='?',default=60,
        help='Time of each frame, in seconds (default 60)'
    )
    parser.add_argument(
        'type',type=str,nargs='?',default='geo_10km',
        help='Type of aggregation (default geo_10km)'
    )

    args=parser.parse_args()

    print('Making movie for',args.evid)
    movie=Movie(args)
    exit()


if __name__=='__main__':
    main()



