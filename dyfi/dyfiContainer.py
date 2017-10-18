"""

DyfiContainer
=============

"""

from .config import Config
from .event import Event
from .entries import Entries
from .products import Products

class DyfiContainer:
    """

    :synopsis: Class for handling DyfiContainer objects. This holds all DYFI data about a particular earthquake (event data, entries, aggregated intensities, and products).
    
    """

    def __init__(self,evid,configfile='config.yml'):

        config=Config(configfile)
        self.event=Event(evid,config=config)
        self.entries=Entries(evid,config=config)
        self.products=Products(self.event,self.entries,config=config)

        self.products.createAll()

