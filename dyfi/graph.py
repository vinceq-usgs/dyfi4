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


    def __init__(self,name,event,data,config=None,eventDir=None,title=None,parent=None):

        print('Graph: Creating',name,'object.')

        self.name=name
        self.event=event
        self.config=config
        self.dir=eventDir
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
        rawdata=self.rawdata

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
        #if hasattr(rawdata,'min_x'):
        #    self.params['min_x']=rawdata.min_x
        #if hasattr(rawdata,'max_x'):
        #    self.params['max_x']=rawdata.max_x

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

        datasets=[x for x in self.datasets if x['id']=='scatterdata']
        if len(datasets)>0:
            return datasets[0]

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
            'id':'scatterdata',
            'legend':'Aggregated %s data' % (rawdata.id),
            'class':'scatterplot1',
            'data':xydata
            }

        return scatterdata


    def getIpeData(self,ipelist=None):
        mag=self.event.mag
        min_x=self.params['min_x']
        max_x=self.params['max_x']

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
                'id':'ipe_'+ipe.name,
                'legend':ipe.name,
                'class':'estimated_'+str(counter),
                'data':ipedata
            }
            multipleipes.append(dataset)

        return multipleipes


    def getMeanMedianData(self,scatterdata):

        # Create distance bins in log space and fill them

        xspace=self.getDistBins()
        bindata={}
        for pt in scatterdata['data']:
            x=pt['x']
            y=pt['y']
            xbin=int(np.digitize(x,xspace))

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
            'id':'meanBinned',
            'legend':'Mean intensity in bin',
            'class':'mean',
            'data':means
            },
                {
            'id':'medianBinned',
            'legend':'Median intensity in bin',
            'class':'median',
            'data':medians
            }]


    def getDistBins(self):
        if hasattr(self,'distBins'):
            bins=self.distBins
            return bins

        min_x=self.params['min_x']
        max_x=self.params['max_x']

        xspace=np.logspace(
            np.log10(min_x),np.log10(max_x),num=self.NBINS
        )
        self.distBins=xspace
        return xspace


    def getTitle(self):

        event=self.event
        line1='USGS DYFI: %s' % (event.loc)
        line2='ID:%s' % (event.eventid)

        title=[line1,line2]
        return title


# Methods for plot_numresp
# TODO: Put this in separate function

    def getDataTime(self):
        event=self.event
        rawdata=self.rawdata

        d=[]
        self.datasets=d
        eventTime=event.eventDateTime

        # This is not used right now
        #self.params={
        #    'aggregatetype':rawdata['id'],
        #}
        #if hasattr(rawdata,'min_x'):
        #    self.params['min_x']=rawdata.min_x
        #if hasattr(rawdata,'max_x'):
        #    self.params['max_x']=rawdata.max_x

        count=0
        for time in rawdata['data']:
            dTime=(time-eventTime).total_seconds()
            count+=1

            pt={
                'y':count,
                't_seconds':dTime,
                't_absolute':time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            d.append(pt)

        if len(d)<1:
            bounds=self.getTimeBounds(0)
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

    @classmethod
    def getTimeBounds(cls,t):

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
        return json.dumps(self.data,sort_keys=True,indent=2)


