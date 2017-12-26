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
            if count:
                print('Server:',remote,'files:',count)


    def countRemote(self,remote):
        server=self.config.responses['serverTemplate']
        remoteDir=self.config.responses['remoteDir']
        bin=self.config.executables['ssh']

        server=server.format(server=remote)
        remoteDir=remoteDir.format(server=remote)

        commands=[bin,server,'ls','-1',remoteDir,'|','wc','-l'] 
        if self.verbose:
            print('Command:\n',' '.join(commands))
        results=subprocess.run(commands,stdout=subprocess.PIPE)
      
        count=int(results.stdout)
        return count


    def downloadRemote(self,remote,nodelete=False):
        server=self.config.responses['serverTemplate']
        remoteDir=self.config.responses['remoteDir']
        bin=self.config.executables['sync']
        localDir=self.config.directories['incoming']+'/'

        server=server.format(server=remote)
        remoteDir=remoteDir.format(server=remote)
        serverDir=server+':'+remoteDir+'/.'

        command=[bin,'--exclude','tmp.*','--timeout=60',
            '-ulpotgrz',serverDir,localDir]

        if not nodelete:
            command.insert(1,'--remove-sent-files')

        if self.verbose:
            print('Command:\n',' '.join(command))

        results=subprocess.run(command,stdout=subprocess.PIPE)
        return

