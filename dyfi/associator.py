from .config import Config
from .event import Event
from .db import Db


class Associator:

    def __init__(self,evid,directives,configfile='config.yml'):

        self.replacements=None
        self.directives=directives

        config=Config(configfile)
        self.event=Event(evid,config=config)
        if self.event.isStub:
            print('WARNING: Cannot run a stub event.')
            return

        startdatetime=self.event.eventdatetime
        timewindow=directives['time']
        
        db=Db(config)
        entries=db.loadEntries(evid=evid,startdatetime=startdatetime,
                               timewindow=timewindow,loadSuspect=True)
        print('Associator: Got',len(entries),'entries.')

    def replace(self):
        pass



    
