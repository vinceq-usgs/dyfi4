# API to access USGS Comcat based on code by Mike Hearne (https://github.com/usgs/libcomcat)

import urllib
import json
import socket

class Comcat:

    def __init__(self,config,rawInput=None):

        conf=config.comcat
        self.config=conf
        self.baseUrl=conf['urlbase'].replace('__SERVER__',conf['server'])
        self.timeout=conf['timeout']
        self.error=None
        self.raw=rawInput


    def query(self,query):

        url=self.baseUrl+query+'&jsonerror=true'
        print('Requesting:',url)

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


    def event(self,evid,raw=False,includeSuperseded=False):

        if self.raw:
            contents=self.raw

        else:
            query='format=geojson&includesuperseded=[SUPERCEDED]&eventid=[EVENTID]'
            query=query.replace('[EVENTID]',evid)
            superseded='true' if includeSuperseded else 'false'
            query=query.replace('[SUPERCEDED]',superseded)

            contents=self.query(query)

        if raw:
            return contents

        try:
            contents=json.loads(contents)
        except json.JSONDecodeError as e:
            print('Comcat.event: Malformed contents: '+e.msg)
            return 'BAD'

        # check for error messages
        status=Comcat.checkStatus(contents)
        if status:
           return status

        return contents

    @staticmethod
    def checkStatus(contents):

        if 'metadata' in contents:
            meta=contents['metadata']
            if meta['status']==409 and 'deleted' in meta['error']:
                return 'DELETED'
            if meta['status']==404 and 'Not Found' in meta['error']:
                return 'NOT FOUND'

        return None 

