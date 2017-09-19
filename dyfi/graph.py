"""

graph
====

"""

import json
import math
import numpy as np
import copy

from geopy.distance import great_circle
from statistics import mean,median,stdev

from .thirdparty.gmtcolormap import GMTColorMap
from . import ipes

# TODO: Make dist_vs_intensity, time_vs_nresp subclasses of Graph

class Graph:
    """
        :synopsis: Create a static graph
        :param str filename: The filename to create
        :param Event event: An Event object
        :param dict mapparams: A dict of params from a eventMap
        :param dict data: Aggregated data in GeoJSON format
        
    """
        
    NBINS=10 # Number of bins for mean and median data plots
    ipelist=[ipes.aww2014wna,ipes.aww2014ena]
    graphLabels={
        'dist_vs_intensity':{
            'title':'Intensity vs. Distance Plot',
            'xlabel':'Hypocentral distance (km)',
            'ylabel':'Intensity (MMI)'},
        'time_vs_responses':{
            'title':'Time vs. Responses Plot',
            'xlabel':'Responses',
            'ylabel':'Time (sec)',
            }
        }
        
        
    def __init__(self,name,event,data,config=None,dir=None,title=None,parent=None):

        print('Graph: Creating',name,'object.')

        self.name=name
        self.event=event
        self.config=config
        self.dir=dir
        self.rawdata=copy.deepcopy(data)
        self.data=None
        self.datasets=None
        self.title=None

        if 'plot_atten' in name:
            self.getDataDistance()
        
        elif 'plot_numresp' in name:
            self.getDataTime()
            
        else:
            raise NameError('ERROR: Graph got unknown graph type '+name) 

        self.title=title if title else self.getTitle()
        
# Methods for plot_atten
# TODO: Put this in separate function

    def getDataDistance(self):
        event=self.event
        rawdata=self.rawdata
      
        print('Graph.getDataDistance:')

        d=[]
        self.datasets=d
       
        self.params={
            'aggregatetype':rawdata['id'],
            'min_x':1,
            'max_x':1000,
            'min_y':1,
            'max_y':10
        }

        # This is not used right now
        if hasattr(rawdata,'min_x'):
            self.params['min_x']=rawdata.min_x
        if hasattr(rawdata,'max_x'):
            self.params['max_x']=rawdata.max_x
            
        # Add scatter data from aggregated entries

        scatterdata=self.getScatterData()
        d.append(scatterdata)
        d.extend(self.getMeanMedianData(scatterdata))
        if hasattr(self.event,'mag'):
            d.extend(self.getIpeData())

        self.data={
            'datasets':d,
            'xlabel':'Hypocentral distance (km)',
            'ylabel':'Intensity (MMI)',
            'title':'Intensity vs. Distance Plot'
        }
            
            
    def getScatterData(self):
        event=self.event
        rawdata=self.rawdata
    
        print('Graph.getScatterData:')
        if hasattr(rawdata,'scatterdata'):
            return rawdata.scatterdata

        epicenter=(event.lat,event.lon)
        xydata=[]

        for loc in rawdata.features:
            loccoords=loc.properties['center']['coordinates']
            x=great_circle(epicenter,reversed(loccoords)).kilometers
            x=float('%.1f' % x)

            pt={
                'x':float('%.1f' % x),
                'y':loc.properties['intensity']
                }
            xydata.append(pt)

        scatterdata={
            'legend':'Aggregated %s data' % (rawdata.id),
            'class':'scatterplot1',
            'data':xydata
            }

        return scatterdata
        

    def getIpeData(self,ipelist=None):
        mag=self.event.mag
        min_x=self.params['min_x']
        max_x=self.params['max_x']

        print('Graph.getIpeData:')
        if not ipelist:
            ipelist=self.ipelist

        multipleipes=[]
        
        counter=0
        for ipe in ipelist:
            counter+=1
            
            ipedata=[]
            xspace=np.logspace(
                np.log10(min_x),
                np.log10(max_x),
                num=50
                )
            
            ipedata=[{'x':float('%.2f' % (x)),
                      'y':float('%.2f' % (ipe(mag,x,fine=True)))
                      } for x in xspace]
            
            dataset={
                'legend':ipe.name,
                'class':'estimated_'+str(counter),
                'data':ipedata
            }
            multipleipes.append(dataset)
        
        return multipleipes

    
    def getMeanMedianData(self,scatterdata):

        # Create distance bins in log space and fill them
        print('Graph.getMeanMedianData:')

        xspace=self.getDistBins()
        bindata={}
        for pt in scatterdata['data']:
            x=pt['x']
            y=pt['y']
            xbin=int(np.digitize(pt['x'],xspace))

            if xbin in bindata:
                bindata[xbin].append(y)
            else:
                bindata[xbin]=[y]

        print('Graph: Got %i pts into %i bins' % (
                len(scatterdata['data']),len(bindata)))

        means=[]
        medians=[]
        for n in range(1,len(xspace)):
            if n not in bindata:
                continue

            xcenter=math.sqrt(xspace[n-1]*xspace[n])
            ydata=bindata[n]
                
            # Create median dataset
            medianpt={
                'x':round(xcenter,1),
                'y':round(median(ydata),2),
                'min_x':round(xspace[n-1],1),
                'max_x':round(xspace[n],1)
                }
            medians.append(medianpt)
            
            # Create mean dataset
            
            if len(ydata)>1:
                y_stdev=stdev(ydata)
            else:
                y_stdev=0

            meanpt={
               'x':round(xcenter,2),
                'y':round(mean(ydata),1),
                'min_x':round(xspace[n-1],2),
                'max_x':round(xspace[n],1),
                'stdev':round(y_stdev,1)
                }
            means.append(meanpt)
                          
        return [{
            'legend':'Mean intensity in bin',
            'class':'mean',
            'data':means
            },
                {
            'legend':'Median intensity in bin',
            'class':'median',
            'data':medians
            }]

    
    def getDistBins(self):
        
        print('Graph.getDistBins:')
        if hasattr(self,'distBins'):
            return self.distBins
        
        min_x=self.params['min_x']
        max_x=self.params['max_x']

        xspace=np.logspace(
            np.log10(min_x),np.log10(max_x),num=self.NBINS
        )
        self.distBins=xspace
        return xspace


    def getTitle(self):

        print('Graph.getTitle:')       
        event=self.event
        line1='USGS DYFI: %s' % (event.loc)
        line2='ID:%s' % (event.eventid)
                                                 
        title=[line1,line2]
        return title
        
        
    def getTicks(self):
        # TODO: Make these configurable
        
        min_x=self.params['min_x']
        max_x=self.params['max_x']
        ax.set_xlim([min_x,max_x])
        ax.set_ylim([1,9])
        ax.semilogx(subsx=None)

        # This changes the ticks on the log scale
        xticks=[1,5,10,20,50,100,200,500,1000,2000,5000,10000]
        xticks=[x for x in xticks if x>=min_x and x<=max_x]
        
        return filename
     
    
# Methods for plot_numresp
# TODO: Put this in separate function

    def getDataTime(self):
        event=self.event
        rawdata=self.rawdata
     
        print('Graph.getDataTime:')

        d=[]
        self.datasets=d
        eventTime=event.eventDateTime

        # This is not used right now
        self.params={
            'aggregatetype':rawdata['id'],
        }
        if hasattr(rawdata,'min_x'):
            self.params['min_x']=rawdata.min_x
        if hasattr(rawdata,'max_x'):
            self.params['max_x']=rawdata.max_x

        count=0
        for time in rawdata['data']:
            dTime=(time-eventTime).total_seconds()
            count+=1

            if len(d)>0 and d[-1]['t_seconds']==dTime:
                continue

            pt={
                'x':None,
                'y':count,
                't_seconds':dTime,
                't_absolute':time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            d.append(pt)

        if len(d)<1:
            bounds=self.getTimebounds(0)
        else:
            bounds=self.getTimeBounds(d[-1]['t_seconds'])

        prefUnit=bounds['prefUnit']
        prefConversion=bounds['prefConversion']

        for pt in d:
            pt['x']=round(pt['t_seconds']/prefConversion,2)

        self.data={
            'datasets':{
                'class':'histogram',
                'data':d
            },
            'xlabel':'Time since earthquake (%s)' % prefUnit,
            'ylabel':'Number of responses',
            'title':'Responses vs. Time Plot',
            'preferred_unit':prefUnit,
            'preferred_conversion':prefConversion,
            'eventid':event.eventid
        }
          
    def getTimeBounds(self,t):

        if t<120:
            unit='minutes'
            conversion=60

        else:
            unit='hours'
            conversion=3600

        return {
            'prefUnit':unit,
            'prefConversion':conversion
        }


# Methods for all Graph objects

    def toJSON(self):
        print('Graph.toJSON:')
        return json.dumps(self.data,sort_keys=True,indent=2)

 
    def getColor(self,intensity):
        if not self.colors:
            return 0
        hexcolor=self.colors.getHexColor(intensity)
        return hexcolor[0]
        
        
  # Below these are class methods

    def distanceData(event,data):
        print('Graph labels:')

        datasets=[]
        dist_vs_int=[]
        
        reporteddata=[]        
        for loc in data:
            y=loc.properties['intensity']
            x=great_circle(
                (event.latitude,event.longitude),
                loc.properties['center'])
            pt={
                'x':round(x,2),
                'y':round(x,1),
                }
            dist_vs_int.append(pt)
        
        datasets.append({
                'legend':'All reported data',
                'data':dist_vs_int,
                'class':'scatterplot1'
                })
        
        ipecounter=0
 
    
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
    
