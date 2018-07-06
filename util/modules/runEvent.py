import sys
import os.path

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')))
from dyfi import Event

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'.')))
from modules.runDb import RunDb

class RunEvent(Event):

    def __init__(self,event,config=None,missing_ok=False):
        Event.__init__(self,event,config,missing_ok)


    @staticmethod
    def createFromContents(contents):
        if not contents:
            return

        if 'metadata' in contents:
            meta=contents['metadata']
            if 'error' in meta:
                return meta['error']

        rawdata={'id':contents['id']}

        relevant=['place','time','mag','ids','net']
        for key in relevant:
            rawdata[key]=contents['properties'][key]

        coords=['lon','lat','depth']
        rawdata.update(zip(coords,contents['geometry']['coordinates']))

        # TODO: Update event_version, code_version
        rawdata['eventdatetime']=RunDb.epochToString(rawdata['time']/1000)
        rawdata['createdtime']=RunDb.epochToString()

        # Now turn raw values into table values

        conversion={
            'eventid':'id',
            'loc':'place',
            'source':'net',
            'orig_id':'id'
        }

        converted={}
        for key in RunEvent.columns:
            if key in rawdata:
                converted[key]=rawdata[key]
            elif key in conversion:
                converted[key]=rawdata[conversion[key]]
            else:
                converted[key]=None

        event=Event(converted)

        dups=RunEvent.readDuplicatesFromContents(contents)
        if dups:
            event.duplicates=dups

        return event


    @classmethod
    def readDuplicatesFromContents(self,contents):
        if 'properties' in contents and 'ids' in contents['properties']:
            duptext=contents['properties']['ids']
        else:
            return

        dups=[]
        goodid=contents['id']
        for tryid in duptext.split(','):
            if not tryid or tryid=='': continue
            if tryid==goodid: continue
            dups.append(tryid)

        if dups:
            return dups


