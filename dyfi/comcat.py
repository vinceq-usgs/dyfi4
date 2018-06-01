import urllib
import json

class Comcat:

    def __init__(self,config):

        conf=config.comcat
        self.config=conf
        self.baseUrl=conf['urlbase'].replace('__SERVER__',conf['server'])
        self.timeout=conf['timeout']


    def query(self,query):

        url=self.baseUrl+query
        print('Requesting:',url)

        try:
            contents=urllib.request.urlopen(url,timeout=self.timeout).read().decode('utf8')

#        except urllib.error.URLError as e:
#            print(e.reason)

#            contents=None

        except urllib.error.HTTPError as e:
            for key in e.__dict__:
                val=e.__dict__[key]
#                print(key,':',val)

            print(e.file.read())
            print(e.file.msg)

            contents=None
            exit()
        except:
            raise
        self.contents=contents
        return contents


    def event(self,evid,includeSuperseded=False):

        QUERY='format=geojson&includesuperseded=[SUPERCEDED]&eventid=[EVENTID]'
        query=QUERY.replace('[EVENTID]',evid)
        superseded='true' if includeSuperseded else 'false'
        query=query.replace('[SUPERCEDED]',superseded)

        contents=self.query(query)
        if contents:
            try:
                contents=json.loads(contents)
            except json.JSONDecodeError as e:
                print('Possible malformed contents: '+e.msg)
                return

        self.contents=contents
        return contents

