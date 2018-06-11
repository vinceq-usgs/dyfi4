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

          (in dyfiContainer)

          filter=Filter(event,config).filterFunction()
          entries=Entries(event,config,filter)

          (in Entries)

          for location in locations.features:
            result=filter(location[,addDistance=True])
            if not bad:
                # store this

        Result values:
        null : good
        1 : greater than ipe threshold
        2 : greater than maxdist

        By default, this will modify location by adding properties['dist']

    """

    def __init__(self,event,config,ipe='aww2014ena'):

        self.event=event
        self.config=config.filter

        if ipe:
            self.ipe=getattr(ipes,ipe)

        print('Filter: Using IPE',ipe)


    def filterFunction(self,addDistance=True):
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


        # This is the function returned by filterFunction()
        def func(entry,debug=False):

            # Get coordinates
            if 'properties' in entry and 'center' in entry['properties']:
                loccoords=entry['properties']['center']['coordinates']
                loccoords=list(loccoords)
                loccoords.reverse()

            else:
                print(entry)
                raise ValueError('Cannot find coordinates')

            # Hypocentral distance
            r=dist(epicenter,loccoords,edepth)

            if addDistance:
                entry['properties']['dist']=round(r,1)

            # Is this greater than the maximum possible distance?
            if r>config['maxdist']:
                return 2

            # If there are lots of responses, do not filter
            if 'nresp_do_not_filter' in config and 'nresp' in entry['properties']:
                threshold=config['nresp_do_not_filter']
                nresp=entry['properties']['nresp']
                if nresp>=threshold:
                    return 0

            if self.ipe:

                # Is expected int at this dist < int_low_threshold?
                expectedI=self.ipe(emag,r,fine=True)
                if expectedI<config['int_low_threshold']:
                    return 1

                # Is this this intensity > exp_I + threshold?
                ii=entry['properties']['intensityFine']
                if ii>(expectedI+config['int_diff_threshold']):
                    return 1

            return

        return func



