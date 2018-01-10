"""

Filter.py
=========

"""

from geopy.distance import great_circle
import math
from . import ipes
class Filter:
    """

        Returns a filter function
        Usage:
        filter=Filter(event,config).filterFunction()
        result=filter(entry)

        result values:
        null : good
        1 : greater than ipe threshold
        2 : greater than maxdist

    """

    def __init__(self,event,config,ipe='aww2014wna'):

        self.event=event
        self.config=config.filter

        if ipe:
            self.ipe=ipes.__dict__[ipe]


    def filterFunction(self):
        """
        Returns a function

        """

        config=self.config

        epicenter=(self.event.lat,self.event.lon)
        edepth=self.event.depth
        emag=self.event.mag


        def dist(latlon1,latlon2,depth):
            r=great_circle(latlon1,latlon2).kilometers
            if edepth:
                r=math.sqrt(r**2+edepth**2)
            return r


        def func(entry):

            # Get coordinates
            if 'properties' in entry and 'center' in entry['properties']:
                loccoords=entry['properties']['center']['coordinates']
                loccoords=list(loccoords)
                loccoords.reverse()

            else:
                print(entry)
                raise ValueError('Cannot find coordinates')

            # Check maximum distance
            r=dist(epicenter,loccoords,edepth)
            if r>config['maxdist']:
                return 2

            ii=entry['properties']['intensity']
            if self.ipe:
                expectedI=self.ipe(emag,r,fine=True)

            # Check distance based on IPE
            if expectedI<config['int_low_threshold']:
                return 1

            # Check max intensity based on IPE
            if ii:
                if ii>(expectedI+config['int_diff_threshold']):
                    return 1

            return

        return func



