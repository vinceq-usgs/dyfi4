# API to access USGS Geoserve based on code by Mike Hearne (https://github.com/usgs/libcomcat)

import urllib
import json
import socket

class Geoserve:

    def __init__(self,config,rawInput=None):

        conf=config.geoserve
        self.config=conf
        self.baseUrl=conf['urlbase'].replace('__SERVER__',conf['server'])
        self.timeout=conf['timeout']
        self.error=None
        self.verbose=None
        self.raw=rawInput
        self.contents=None
        self.name=None
        self.names=None


    def query(self,query):

        url=self.baseUrl+query
        if self.verbose:
            print(url)

        try:
            contents=urllib.request.urlopen(url,timeout=self.timeout).read().decode('utf8')

        except urllib.error.URLError as e: # pragma: no cover
            self.error=e.reason
            contents=None

        except socket.timeout: # pragma: no cover
            print('WARNING: Request timed out.')
            self.error='timeout'
            contents=None

        self.contents=contents
        return contents


    def queryFeature(self,feature):

        result=None
        coords=feature['geometry']['coordinates'][0]
        try:
            result=self.queryBox(coords)

        except ValueError:
            pass

        if result:
            return result

        (lon,lat)=feature['properties']['center']['coordinates']
        name=self.queryPoint(lat,lon)
        return name


    def queryBox(self,coordinates,minpop=100):
        if self.raw:
            self.contents=self.raw

        else:
            minlat=999
            minlon=999
            maxlat=-999
            maxlon=-999

            for coord in coordinates:
                (lon,lat)=coord
                minlat=min(minlat,lat)
                maxlat=max(maxlat,lat)
                minlon=min(minlon,lon)
                maxlon=max(maxlon,lon)

            query='minlatitude=%s&maxlatitude=%s&minlongitude=%s&maxlongitude=%s&type=geonames&minpopulation=%i' % (minlat,maxlat,minlon,maxlon,minpop)
            self.contents=self.query(query)

        if not self.parseName():
            raise ValueError('No name found inside polygon')
        return self.name


    def queryPoint(self,lat,lon,distance=100,population=100,limit=10):
        if self.raw:
            self.contents=self.raw

        else:
            query='latitude=%f&longitude=%f&maxradiuskm=%i&minpopulation=%i&limit=%i' % (lat,lon,distance,population,limit)
            self.contents=self.query(query)

        if not self.parseName(byDistance=True):
            raise ValueError('No name found near point')
        return self.name


    def parseName(self,byDistance=False):

        self.names=[]
        self.name=None

        contents=self.contents
        if not contents:
            return

        try:
            contents=json.loads(contents)
        except json.JSONDecodeError as e:
            print('Geoserve.names: Malformed contents: '+e.msg)
            self.error='Bad JSON'
            raise ValueError(self.error)

        # check for error messages
        # will raise exception if an error is found
        self.contents=contents
        status=self.checkStatus()
        if status:
            raise ValueError(status)

        features=contents['geonames']['features']
        if not features:
            return

        if byDistance:
            sortby='dist'
            reverseSort=False
        else:
            sortby='pop'
            reverseSort=True

        for feature in features:
            p=feature['properties']
            self.names.append({'name':p['name'],'pop':p['population'],'dist':p['distance']})

        self.names=sorted(self.names,key=lambda k:k[sortby],reverse=reverseSort)
        self.name=self.names[0]['name']
        if byDistance:
            self.name='Near '+self.name

        return self.name


    def checkStatus(self):

        self.error=None
        contents=self.contents

        if 'metadata' in contents and 'error' in contents['metadata']:

            error=contents['metadata']['error']
            print('Geoserve: Error code: %i %s' % (error['code'],error['message']))

            self.error=error['message']
            return self.error

