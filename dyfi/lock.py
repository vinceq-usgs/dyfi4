"""

Simple lockfiles using flock
Allows processes to run in crontab without worrying about multiple instances

Usage:
try:
    Lock('program_name',flagDir=['optional directory'])

except:
    exit()

"""

import os.path
import atexit
import fcntl

class Lock:

    def __init__(self,name,flagDir='./flags'):

        self.lockfile='%s/%s.lock' % (flagDir,name)
        self.name=name
        self.f=None

        if not os.path.isdir(flagDir):
            os.makedirs(flagDir,exist_ok=True)

        try:
            self.f=open(self.lockfile,'wb')
            fcntl.flock(self.f,fcntl.LOCK_EX | fcntl.LOCK_NB)
            atexit.register(self.removeLock)

        except:
            print('Lock: Could not lock "%s", stopping.' % self.name)
            exit()


    def removeLock(self):
        print('Lock: removing lock "%s"' % self.name)
        fcntl.flock(self.f,fcntl.LOCK_UN)
        os.remove(self.lockfile)

