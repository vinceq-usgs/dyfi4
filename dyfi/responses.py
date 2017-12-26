"""

Process loop:

Download responses
For each response:
  Write to extended table
  If event doesn't exist in table:
    Save stub in event table (invisible=1)
    Run getEvent.py (separate process)
    

"""

import sys
import argparse
import os
import time
import subprocess
import re

from .config import Config
from .db import Db

class Responses:

    def __init__(self,configfile,verbose=False):

        self.config=Config(configfile)
        self.verbose=verbose
        self.verbose=1
        self.processed=0
        self.downloaded=0

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
        results=subprocess.run(command,stdout=subprocess.PIPE)
        out=results.stdout.decode('utf-8')

        try:
            pattern=re.compile(r'Number of files transferred: (.+?)$',re.MULTILINE)
            found=pattern.search(out).group(1)
            found=int(found)
        except AttributeError:
            found=None

        return found

