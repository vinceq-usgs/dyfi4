"""

plotgraph
====

"""

import math
import numpy as np
from geopy.distance import great_circle
from statistics import mean,median,stdev

import matplotlib.ticker as Ticker
import matplotlib.pyplot as Pyplot
from matplotlib.patches import Polygon,Circle

from .thirdparty.gmtcolormap import GMTColorMap
import .ipes as ipes

# TODO: Make PlotGraph a subclass of Product
# TODO: Make dist_vs_intensity, time_vs_nresp subclasses of PlotGraph

class PlotGraph:
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
        
        
    def __init__(self,event,graphtype,data,title=None,showPlot=False):
        self.event=event
        self.rawdata=data
  
        if graphtype=='dist_vs_intensity':
            self.getDataDistance()
        
        elif graphtype=='time_vs_responses':
            self.getDataTime()
            
        else:
            raise NameError('ERROR: PlotGraph got unknown graph type'+graphtype) 

        if title:
            self.title=title
        else:
            self.title=self.getTitle()

        try:
            self.colors=GMTColorMap.loadFromCPT('./lib/mmi.cpt')
        except:
            self.colors=None
            print('WARNING: Could not load MMI colors')
        
    def getColor(self,intensity):
        if not self.colors:
            return 0
        hexcolor=self.colors.getHexColor(intensity)
        return hexcolor[0]
        
        
    def getDataDistance(self):
        event=self.event
        rawdata=self.rawdata
        
        d=[]
        self.datasets=d
        
        self.params={
            'aggregatetype':rawdata.id,
            'min_x':1,
            'max_x':1000,
            'min_y':1,
            'max_y':10
        }
        if hasattr(rawdata,'min_x'):
            self.params['min_x']=rawdata.min_x
        if hasattr(rawdata,'max_x'):
            self.params['max_x']=rawdata.max_x
            
        # Add scatter data from aggregated entries

        scatterdata=self.getScatterData()
        d.append(scatterdata)
        d.extend(self.getMeanMedianData(scatterdata))
        if hasattr(self.event,'mag'):
            d.extend(self.getIpeData(PlotGraph.ipelist))

        return d
            
            
    def getScatterData(self):
        event=self.event
        rawdata=self.rawdata
        
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
        

    def getIpeData(self,ipelist):
        mag=self.event.mag
        min_x=self.params['min_x']
        max_x=self.params['max_x']

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
            
            ipedata=[{'x':float('%.4f' % (x)),
                      'y':float('%.4f' % (ipe(mag,x,fine=True)))
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

        print('PlotGraph: Got %i pts into %i bins' % (
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
                'x':xcenter,
                'y':median(ydata),
                'min_x':xspace[n-1],
                'max_x':xspace[n]
                }
            medians.append(medianpt)
            
            # Create mean dataset
            
            if len(ydata)>1:
                y_stdev=stdev(ydata)
            else:
                y_stdev=0
            meanpt={
               'x':xcenter,
                'y':mean(ydata),
                'min_x':xspace[n-1],
                'max_x':xspace[n],
                'stdev':y_stdev
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
        
        if hasattr(self,'distBins'):
            return self.distBins
        
        min_x=self.params['min_x']
        max_x=self.params['max_x']

        xspace=np.logspace(
            np.log10(min_x),np.log10(max_x),num=PlotGraph.NBINS
        )
        self.distBins=xspace
        return xspace


    def getTitle(self):
        event=self.event
        line1='USGS DYFI: %s' % (event.loc)
        line2='ID:%s' % (event.eventid)
                                                 
        title=[line1,line2]
        return title
        
        
    def save(self,filename,showPlot=None):
        
        self.fig=Pyplot.figure(dpi=250)
        ax=self.fig.add_subplot(111)
        self.ax=ax

        # TODO: Make these configurable
        
        min_x=self.params['min_x']
        max_x=self.params['max_x']
        ax.set_xlim([min_x,max_x])
        ax.set_ylim([1,9])
        ax.semilogx(subsx=None)

        # This changes the ticks on the log scale
        xticks=[1,5,10,20,50,100,200,500,1000,2000,5000,10000]
        xticks=[x for x in xticks if x>=min_x and x<=max_x]
        self.ax.set_xticks(xticks)
        self.ax.get_xaxis().set_major_formatter(Ticker.ScalarFormatter())
        
        # Plot title(s)
        if isinstance(self.title,str):
            Pyplot.title(self.title,size='medium')
        else:
            title=Pyplot.suptitle(self.title[0],size='small',y=0.96)
            Pyplot.title(self.title[1],size='xx-small')
        
        self.plotData(self.ax,self.datasets)
        ax.legend(loc='upper right',fontsize=10)
        
        if showPlot:
            try:
                Pyplot.show()

            except:
                pass

        Pyplot.savefig(filename,dpi=250)
        Pyplot.close()
        
        return filename
     
    
    def plotData(self,ax,datasets):
        """
            :synopsis:
            :param m: A map object returned by Basemap
        """

        print(ax)

        for dataset in datasets:
            thisclass=dataset['class']
            thisdata=dataset['data']
            thislegend=dataset['legend']
            x=[d['x'] for d in thisdata]
            y=[d['y'] for d in thisdata]

            if 'scatterplot' in thisclass:
                color=[self.getColor(y) for y in y]
                ax.scatter(x,y,c=color,label=thislegend,edgecolors='none')
                
            elif 'mean' in thisclass:
                yerror=[d['stdev'] for d in thisdata]
                ax.errorbar(x,y,yerr=yerror,fmt='none',ecolor='black',
                            label='Std.dev in bin',barsabove=False,zorder=1)
                ax.scatter(x,y,c='red',s=100,label=thislegend,edgecolors='black',zorder=3)

            elif 'median' in thisclass:
                ax.scatter(x,y,c='blue',s=100,label=thislegend,edgecolors='black',zorder=2)
                
            elif 'estimated' in thisclass:
                print(x)
                print(y)
                ax.plot(x,y,label=thislegend)

                
            else:
                print('Unknown class',thisclass,'in plotData.')
                exit()

                
                
        """
        for pt in data.features:

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
                    
            col=self.getColor(intensity)
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
        """
        
    
    # Below these are class methods

    def distanceData(event,data):
        print('Graph labels:')
        print(PlotGraph.graphLabels)

        datasets=[]
        x_vs_y=[]
        
        reporteddata=[]        
        for loc in data:
            y=loc.properties['intensity']
            x=great_circle(
                (event.latitude,event.longitude),
                loc.properties['center'])
            pt={
                'x':x,
                'y':y
                }
            x_vs_y.append(pt)
        
        datasets.append({
                'legend':'All reported data',
                'data':x_vs_y,
                'class':'scatterplot1'
                })
        
        ipecounter=0
 
        exit()
            
    
    
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
    
