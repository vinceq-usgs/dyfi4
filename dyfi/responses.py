"""

Responses
=========

"""

import sys
import argparse
import os
import shutil
import time
import subprocess
import re
import datetime

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


    def downloadServers(self,nodelete=False,checkonly=False):

        remotes=self.config.responses['remotes']

        for remote in remotes.split(','):

            if checkonly:
                count=self.countRemote(remote)
                print('Server:',remote,'files:',count)
                continue

            count=self.downloadRemote(remote,nodelete)
            print('Server:',remote,'files:',count)


    def countRemote(self,remote):
        server=self.config.responses['serverTemplate']
        remoteDir=self.config.responses['remoteDir']
        ssh=self.config.executables['ssh']

        server=server.format(server=remote)
        remoteDir=remoteDir.format(server=remote)

        commands=[ssh,server,'ls','-1',remoteDir,'|','wc','-l'] 
        if self.verbose:
            print('Command:\n',' '.join(commands))
        results=subprocess.run(commands,stdout=subprocess.PIPE)
      
        count=int(results.stdout)
        return count


    def downloadRemote(self,remote,nodelete=False):
        server=self.config.responses['serverTemplate']
        remoteDir=self.config.responses['remoteDir']
        sync=self.config.executables['sync']
        localDir=self.config.directories['incoming']+'/'

        server=server.format(server=remote)
        remoteDir=remoteDir.format(server=remote)
        serverDir=server+':'+remoteDir+'/.'

        command=[sync,'--exclude','tmp.*','--timeout=60',
            '-ulpotgrz','--stats',serverDir,localDir]

        if not nodelete:
            command.insert(1,'--remove-sent-files')

        if self.verbose:
            print('Command:\n',' '.join(command))

        # subprocess encoding is in python 3.6+ only
        # For 3.5, need to use str.decode()
        results=subprocess.run(command,stdout=subprocess.PIPE)
        out=results.stdout.decode('utf-8')

        try:
            pattern=re.compile(r'Number of files transferred: (.+?)$',re.MULTILINE)
            found=pattern.search(out).group(1)
            found=int(found)
        except AttributeError:
            found=None

        return found

    """

    if checkEvid, get authoritative id for this eventid.
    if different, change entry's eventid.
    increment the latest eventid.

    """

    def processFile(self,file,checkEvid=True,save=True):
        entry=self.readFile(file)

        if save or checkEvid:
            if not self.db:
                self.db=Db(self.config)

        evid=entry.eventid
        if checkEvid:
            goodid=self.db.incrementEvid(evid,checkAuth=True)
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

            (k,v)=val.split('=')
            if k in Responses.translateColumns:
                data[Responses.translateColumns[k]]=v
            else:
                print('Unknown key',k)

        # Keys that require special processing

        # 1. Unknown evid
        evid=data['eventid']
        data['orig_id']=evid
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


    def removeFile(self,file):
        badDir=self.config.directories['badincoming']
        os.makedirs(badDir,exist_ok=True)

        return shutil.move(file,badDir)



