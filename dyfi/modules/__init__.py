print("Now in modules __init__")
#print("Importing .thirdparty")
#from .thirdparty.utm.conversion import to_latlon
#from .thirdparty import utm
#print("Done importing .thirdparty")
from .config import Config
print(Config)
from .thirdparty.gmtcolormap import GMTColorMap
from .db import Db
from .event import Event
from .maps import Maps
from .entries import Entries
from .products import Products
from .plotmap import PlotMap
from .plotgraph import PlotGraph
print("Done with modules __init__")
