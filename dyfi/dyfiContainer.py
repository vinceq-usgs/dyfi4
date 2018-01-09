from .config import Config
from .event import Event
from .entries import Entries
from .products import Products

class DyfiContainer:
    """

    :synopsis: Class for handling DyfiContainer objects
    
    This holds all the DYFI data about a particular event: event data, entries, aggregated intensities, and products.

    .. py:attribute:: event

        A :py:obj:`dyfi.event.Event` object.

    .. py:attribute:: entries

        A :py:obj:`dyfi.entries.Entries` object.

    .. py:attribute:: products

        A :py:obj:`dyfi.products.Products` object.

    """

    def __init__(self,evid,configfile='config.yml'):

        config=Config(configfile)
        self.event=Event(evid,config=config)

        self.entries=Entries(event=self.event,config=config)
        self.products=Products(self.event,self.entries,config=config)
        self.products.createAll()


    def resetReponsesCount():
        pass

