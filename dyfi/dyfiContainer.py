from .config import Config
from .event import Event
from .entries import Entries
from .filter import Filter
from .products import Products

class DyfiContainer:
    """

    :synopsis: Class for handling DyfiContainer objects
    :param str evid: Event ID
    :param str configfile: YAML file with configuration options (default `./cofig.yml`)

    This implements a container for all DYFI data about a particular event: event data, entries, aggregated intensities, and products. 
    
    Creating an instance also initiates DYFI processing:

    1. Load event data for this event ID from the database.
    2. Load entries from the database, aggregate the entries, and filter them.
    3. Create products from the data.

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

        cdifilter=Filter(event=self.event,config=config).filterFunction()
        self.entries=Entries(event=self.event,config=config,cdifilter=cdifilter)

        self.products=Products(self.event,self.entries,config=config)
        self.products.createAll()

