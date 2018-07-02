"""

Incoming
=========

"""

import sys
import os
import urllib.parse

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')))
from dyfi import Db,Event,Entry
from dyfi.cdi import calculate as CdiCalculate

#from .db import Db
#from .event import Event
#from .entries import Entry
#from .cdi import calculate as CdiCalculate

class Incoming:

    translateColumns={
        'server' : 'server',
        'eventid' : 'eventid',
        'eventTime' : 'event_time',
        'language' : 'language',
        'd_text' : 'd_text',
        'orig_id' : 'orig_id',

        'fldSituation_felt' : 'felt',
        'fldSituation_others' : 'other_felt',
        'fldSituation_situation' : 'situation',
        'fldSituation_sitOther' : 'situation',
        'fldSituation_structure' : 'building',
        'fldSituation_structOther' : 'building',
        'fldSituation_sleep' : 'asleep',

        'fldExperience_shaking' : 'motion',
        'fldExperience_duration' : 'duration',
        'fldExperience_reaction' : 'reaction',
        'fldExperience_response' : 'response',
        'response_other' : 'response',
        'fldExperience_stand' : 'stand',

        'fldEffects_doors' : 'sway',
        'fldEffects_sounds' : 'creak',
        'fldEffects_shelved' : 'shelf',
        'fldEffects_pictures' : 'picture',
        'fldEffects_furniture' : 'furniture',
        'fldEffects_appliances' : 'heavy_appliance',
        'fldEffects_walls' : 'walls',

        'fldDamage_structure' : 'building_details',

        'fldContact_name' : 'name',
        'fldContact_email' : 'email',
        'fldContact_phone' : 'phone',
        'fldContact_comments' : 'comments',

        'timestamp' : 'time_now',
        'ciim_time' : 'usertime',
        'ciim_report' : 'report',

        'ciim_mapConfidence' : 'confidence',
        'form_version' : 'version',
        'ciim_mapAddress' : 'street',
        'ciim_mapRegion' : 'admin_region',
        'ciim_mapCity' : 'city',
        'ciim_mapCountry' : 'country',
        'ciim_mapLat' : 'latitude',
        'ciim_mapLon' : 'longitude',
        'ciim_mapZip' : 'zip'
}

    def __init__(self,config,verbose=False):

        self.config=config
        self.verbose=verbose
        self.processed=0
        self.downloaded=0
        self.db=Db(config)

        os.makedirs(config.directories['incoming'],exist_ok=True)


    def checkIncoming(self):
        incomingDir=self.config.directories['incoming']
        files=next(os.walk(incomingDir))[2]
        files=[incomingDir+'/'+x for x in files]
        return files


    def saveFile(self,rawfile):
        """

        1. Parse data
        2. Check if event exists and has a different good_id
           (if so, correct this entry's evid)
        3. Save entry
        4. Increment event newresponses

        """
        if isinstance(rawfile,dict):
            entry=rawfile
        else:
           entry=self.readFile(rawfile)
        if not entry:
            return

        evid=entry.eventid
        db=self.db

        if evid!='unknown':
            event=Event(evid,config=self.config,missing_ok=True)

            # Does the associated event exist and have a different good_id?
            # Then move this evid to the correct one.
            if event.good_id and evid!=event.good_id:
                goodid=event.good_id
                print('WARNING: switching evid from',evid,'to',goodid)
                evid=goodid
                entry.eventid=goodid

        # Now save
        subid=db.save(entry)
        if not subid:
            print('WARNING: Incoming.saveFile could not save',rawfile)
            return None

        entry.subid=subid

        # Lastly, increment the correct row in the event table
        if evid!='unknown':
            print('Incrementing newresponses for',evid)
            db.setNewresponse(evid,value=1,increment=True)

        return entry


    def readFile(self,rawfile):
        with open(rawfile,'r') as f:
            raw=f.read()

        # Trust that earthquake-dyfi-responses is doing its job
        # and handling characters properly
        # but just in case, don't blindly accept keys

        if '.json' in rawfile:
            rawdata=json.decode(raw)

        else:
            urllib.parse.unquote_plus(raw,encoding='utf-8',errors='replace')
            rawdata=urllib.parse.parse_qs(raw)

        data={}
        for k,v in rawdata.items():

            # parse_qs returns a { k:[v], k:[v], k:[v]... }
            v=v[0]
            if k in self.translateColumns:
                data[self.translateColumns[k]]=v
            else:
                print('Unknown key',k)

        if len(data.keys())==0:
            return

        # Keys that require special processing

        # 1. Unknown evid and orig_id
        if 'eventid' not in data:
            data['eventid']='unknown'

        evid=data['eventid']
        if evid==None or evid=='null':
            evid='unknown'
            data['eventid']=evid

        data['orig_id']=evid

        # 2. Make sure time_now exists
        if 'time_now' not in data or not data['time_now']:
            print('WARNING: Incoming.readFile found no timestamp for',rawfile)
            return
        data['time_now']=Db.epochToString(int(data['time_now']))

        # 3. Rebase longitude
        data['longitude']=self.rebaseLongitude(data['longitude'])

        # 4. Calculate user_cdi
        entry=Entry(data)
        entry.user_cdi=CdiCalculate(entry)

        return entry


    def remove(self,rawfile,bad=False):

        badDir=self.config.directories['trashincoming']
        if bad:
            badDir=self.config.directories['badincoming']
            print('Moving this file to',badDir)

        os.makedirs(badDir,exist_ok=True)
        return os.rename(rawfile,badDir+'/'+os.path.basename(rawfile))


    @staticmethod
    def rebaseLongitude(x):
        if not x: return x
        x=float(x)
        while True:
            if x>180: x-=360
            elif x<-180: x+=360
            else: break

        return str(x)

