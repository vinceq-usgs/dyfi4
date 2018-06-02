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

    def __init__(self,name,flagDir='./flags',silent=False,fail_ok=False):

        self.lockfile='%s/%s.lock' % (flagDir,name)
        self.name=name
        self.f=None
        self.success=False
        self.silent=silent

        os.makedirs(flagDir,exist_ok=True)

        self.f=open(self.lockfile,'wb')
        try:
            fcntl.flock(self.f,fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.success=True
        except BlockingIOError:
            print('Could not create lock for',name)
            if fail_ok:
                self.success=False
                return
            else:
                exit()

        atexit.register(self.removeLock)
        if not silent:
            print('Lock: created lock "%s"' % self.name)


    def removeLock(self):
        if self.lockfile:        
            if not self.silent:
                print('Lock: removing lock "%s"' % self.name)
            fcntl.flock(self.f,fcntl.LOCK_UN)
            os.remove(self.lockfile)
            self.lockfile=None
            

