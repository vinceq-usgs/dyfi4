"""

Incoming
=========

"""

import os
import shutil
import subprocess
import re

from .config import Config
from .db import Db
from .entries import Entry
from .cdi import calculate as CdiCalculate

class Responses:

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

    def __init__(self,configfile,verbose=False):

        self.config=Config(configfile)
        self.verbose=verbose
        self.processed=0
        self.downloaded=0
        self.db=None

        os.makedirs(self.config.directories['incoming'],exist_ok=True)


    def checkIncomingDir(self):
        incomingDir=self.config.directories['incoming']
        files=next(os.walk(incomingDir))[2]
        files=[incomingDir+'/'+x for x in files]
        return files


    def processFile(self,file,checkEvid=True,save=True):
        entry=self.readFile(file)
        if not entry:
            return

        if save or checkEvid:
            if not self.db:
                self.db=Db(self.config)

        evid=entry.eventid
        if checkEvid:

            # This updates the event table newresponses column.
            # It will check if the event
            # has an updated good_id column. If it does, change
            # this entry's evid to the correct one..

            goodid=self.db.checkIncrementEvid(evid)
            if goodid and goodid!=evid:
                entry.eventid=goodid
                evid=goodid

        if save:
            subid=self.db.save(entry)
            if subid:
                entry.subid=subid
                return entry
            else:
                print('WARNING: Responses.processFile could not save',file,'to database')
                return

        return entry

    def readFile(self,file):
        with open(file,'r') as f:
            raw=f.read()

        # Trust that earthquake-dyfi-responses is doing its job
        # and handling characters properly
        # but just in case, don't blindly accept keys

        data={}
        for val in raw.split('&'):
            if '=' not in val:
                continue

            (k,v)=val.split('=')[0:2]
            if k in Responses.translateColumns:
                data[Responses.translateColumns[k]]=v
            else:
                print('Unknown key',k)

        if len(data.keys())==0:
            return

        # Keys that require special processing

        # 1. Unknown evid
        if 'eventid' not in data:
            data['eventid']='unknown'

        evid=data['eventid']
        if evid==None or evid=='null':
            evid='unknown'
            data['eventid']=evid

        # 2. Make sure time_now exists
        if 'time_now' not in data or not data['time_now']:
            print('WARNING: Responses.processFile found no timestamp for',file)
            return
        data['time_now']=Db.epochToString(int(data['time_now']))

        # 3. Calculate user_cdi
        entry=Entry(data)
        entry.user_cdi=CdiCalculate(entry)
        return entry


    def remove(self,file,bad=False):
        badDir=self.config.directories['badincoming']
        os.makedirs(badDir,exist_ok=True)

        return shutil.move(file,badDir)
