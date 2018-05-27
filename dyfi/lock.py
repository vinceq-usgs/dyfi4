"""

Simple lockfiles using flock
Allows processes to run in crontab without worrying about multiple instances

Usage:
Lock('program_name',flagDir=['optional directory']):

[will exit if failed]

"""

import os.path
import atexit
import fcntl

class Lock:

    def __init__(self,name,flagDir='./flags'):

        self.lockfile='%s/%s.lock' % (flagDir,name)
        self.name=name
        self.f=None

        os.makedirs(flagDir,exist_ok=True)

        self.f=open(self.lockfile,'wb')
        try:
            fcntl.flock(self.f,fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Could not create lock for',name)
            exit()

        atexit.register(self.removeLock)
        print('Lock: creating lock "%s"' % self.name)


    def removeLock(self):
        if self.lockfile:        
            print('Lock: removing lock "%s"' % self.name)
            fcntl.flock(self.f,fcntl.LOCK_UN)
            os.remove(self.lockfile)
            self.lockfile=None
            

