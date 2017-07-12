"""

plotmap
====

"""

from math import cos,pi

import numpy as np
import matplotlib.pyplot as Pyplot
from matplotlib.patches import Polygon,Circle
from matplotlib.collections import PatchCollection
#from mpl_toolkits.basemap import Basemap

from . import backgroundImage as BackgroundImage
from . import GMTColorMap


class PlotMap:
    """
        :synopsis: Create a static map
        :param str filename: The filename to create
        :param Event event: An Event object
        :param dict mapparams: A dict of params from a eventMap
        :param dict data: Aggregated data in GeoJSON format
        
    """
    
    def __init__(self,event,data,title=None,maps=None,showPlot=False):
        self.event=event
        self.mapparams=maps
        self.data=data
        self.m=None
        self.fig=None
        
        if not title:
            self.title=self.getTitle()

        self.colors=GMTColorMap.loadFromCPT('./lib/mmi.cpt')
        

    def getTitle(self):
        event=self.event
        print(event)
        
        if event.lat>=0:
            lattext='%.4fN' % (event.lat)
        else:
            lattext='%.4fS' % (-event.lat)

        if event.lon>=0:
            lontext='%.4fE' % (event.lon)
        else:
            lontext='%.4fW' % (-event.lon)
        
        line1='USGS DYFI: %s' % (event.loc)
        line2='%s   M%s   %s %s   Depth:%.1f km   ID:%s' % (
            event.eventlocaltime,event.mag,lattext,lontext,
            float(event.depth),event.eventid
            )
                                                 
        title=[line1,line2]
        return title
        
        
        
    def save(self,filename,showPlot=None):
        
        self.getParams()

        self.fig=Pyplot.figure(dpi=250)
        self.ax=self.fig.add_subplot(111)
        
        # epsg=3857 to match NatGeo_World_Map
#        m=Basemap(projection='merc',
#                  llcrnrlat=self.south,
#                  llcrnrlon=self.west,
#                  urcrnrlat=self.north,
#                  urcrnrlon=self.east,
#                  lat_ts=(self.north+self.south)/2,
#                  epsg=3857,
#                  ellps='WGS84',
#                  fix_aspect=True,
#                  resolution='c')
     
        # This needs to be Cartopy now 
        m={}
        self.m=m
        try:
            BackgroundImage.addImage(self)
        except:
            print('No background image found, continuing.')

        # Plot title(s)
        if isinstance(self.title,str):
            Pyplot.title(self.title,size='medium')
        else:
            title=Pyplot.suptitle(self.title[0],size='small',y=0.96)
            Pyplot.title(self.title[1],size='xx-small')

        #m.drawcoastlines(zorder=3)
        #m.drawmapboundary(fill_color='aqua',zorder=3)
        #m.fillcontinents(color=(0.7,0.7,0.7),
        #                 lake_color='aqua',zorder=3)
        
        # Plot ticks and labels
        m.drawparallels(PlotMap.degreelines(self.south,self.north),
                        labels=[1,0,0,1])
        m.drawmeridians(PlotMap.degreelines(self.west,self.east),
                        labels=[1,0,0,1])

        self.plotData(m)

        # Plot epicenter
        m.plot(self.event.lon,self.event.lat,'k*',
               latlon=True,mew=0.2,markersize=20,
               mfc='red',mec='black',zorder=5)        

        if showPlot:
            try:
                Pyplot.show()

            except:
                pass

        Pyplot.savefig(filename,dpi=250)
        Pyplot.close()
        
        return filename
    
        
    def getParams(self):
        event=self.event
        mp=self.mapparams

        # Used for computing default values
        magnitude=self.event.mag
        producttype=self.data.id
        
        lat_span=0
        lon_span=0
        lat_offset=0
        lon_offset=0
        
        if mp:
            if mp.lat_span:
                lat_span=mp.lat_span
                print('Asserting lat_span',lat_span)
            if mp.lon_span:
                lon_span=mp.lon_span
                print('Asserting lon_span',lon_span)
            if mp.lat_offset:
                lat_offset=mp.lat_offset
            if mp.lon_offset:
                lon_offset=mp.lon_offset
        
        if lon_span==0:
            # Use default values
            if producttype=='geo_10km':
                lon_span=10
            elif producttype=='zip':
                lon_span=5
            elif producttype=='geo_1km':
                lon_span=1
                
        if lat_span==0:
            lat_span=PlotMap.get_latspan(
                event.lat+lat_offset,lon_span)
        
        north=event.lat+lat_offset+lat_span/2
        south=event.lat+lat_offset-lat_span/2
        east=event.lon+lon_offset+lon_span/2
        west=event.lon+lon_offset-lon_span/2
        
        print('PlotMap: bounds lat:%s,%s lon:%s,%s' %
              (south,north,west,east))

        self.north=north
        self.south=south
        self.west=west
        self.east=east

        return
    
    
    def plotData(self,m):
        """
            :synopsis:
            :param m: A map object returned by Basemap
        """
        
        data=self.data
        patches=[]
        colors=[]

        for pt in data.features:

            ### TODO: Plot a Point as a circle

            featuretype=pt.geometry.type
            

            if featuretype=='Point':
                coords=pt.geometry.coordinates
                coords=Plot.transform([coords],m)
                poly=Circle(coords[0],
                             fill=True,radius=10000)

            elif featuretype=='Polygon':
                coords=pt.geometry.coordinates[0]
                coords=PlotMap.transform(coords,m)
                poly=Polygon(np.array(coords),
                             closed=True)
            patches.append(poly)

            if 'intensity' in pt.properties:
                intensity=pt.properties['intensity']
            elif 'cdi' in pt.properties:
                intensity=pt.properties['cdi']
            else:
                intensity=9
                    
            col=self.colors.getHexColor(intensity)[0]
            colors.append(col)

        if patches:
            coll=PatchCollection(
                patches,zorder=4,
                edgecolor='k',
                linewidth=0.2
            )
            coll.set_facecolor(colors)
            self.ax.add_collection(coll)

        return m
        
    
    # Below these are class methods

    
    def get_latspan(lat,lon_span):
        scale=cos(lat*pi/180)
        if scale>2:
            print('WARNING: Plot::get_latspan scale',scale,'.')
            print('WARNING: Plot::get_latspan set to 2.')
            print('WARNING: Plot may not be square.')
            scale=2

        return scale*lon_span
    
    
    def degreelines(a,b):
        aint=int(a)
        bint=int(b+0.5)
        step=1
        if bint-aint>5:
            step=2
        if bint-aint>13:
            step=5
        return range(aint,bint,step)
        

    def transform(coords,m):
        newcoords=[]
        for pt in coords:
            x,y=m(pt[0],pt[1])
            newcoords.append([x,y])
            
        return newcoords
    
