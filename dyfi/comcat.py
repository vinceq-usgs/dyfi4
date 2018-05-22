import urllib.request
import json

class Comcat:

    SERVER = 'earthquake' #comcat server name
    URLBASE = 'https://[SERVER].usgs.gov/fdsnws/event/1/query?'.replace('[SERVER]',SERVER)
    ALLPRODURL = 'https://earthquake.usgs.gov/fdsnws/event/1/query?'

    def __init__(self,query):

        url=Comcat.URLBASE+query+'&format=geojson'
        print('Requesting:')
        print(url)

        try:
            contents=urllib.request.urlopen(url).read().decode('utf8')
        except urllib.error.URLError:
            contents=None
            
        self.contents=contents

    
class ComcatEvent:
    
    QUERY='format=geojson&includesuperseded=[SUPERCEDED]&eventid=[EVENTID]'

    def __init__(self,evid,includeSuperseded=False):
        query=self.QUERY.replace('[EVENTID]',evid)
        if includeSuperseded:
            superseded='true'
        else:
            superseded='false'
            
        query=query.replace('[SUPERCEDED]',superseded)
        contents=Comcat(query).contents
        if contents:
            try:
                contents=json.loads(contents)
            except:
                print('Possible malformed contents from fdsnws')
                return
            
        self.contents=contents

