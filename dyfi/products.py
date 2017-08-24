"""

Products
========

"""

import json
import os
import yaml

from .graph import Graph
from .contents import Contents
from . import staticMap 

class Products:
    """
    
    :synopsis: Handle product generation for an event. This calls other product generators like :py:obj:`Contents` and :py:obj:`PlotMap`.
    :param event: :py:obj:`Event` object
    :param str name: type of product (e.g. 'geo_1km', 'zip')
    
        self.maps=None
        self.entries=entries
        
        self.evid=event.eventid
        self.productDir=product dir
        self.products=[]        

    .. attribute:: evid
    
    The event ID for this product.
    
    .. attribute:: event
    
    A reference to the Event object for this product.

    .. attribute:: maps
    
    A reference to the Maps object which provides custom parameters for this product. (Not yet implemented)

    .. attribute:: entries
    
    A reference to the Entries object for this product.

    .. attribute:: productDir
    
    The location for output files (from :py:obj:`getProductDir`).

    .. attribute:: products
    
    The list of product filenames.
    
    .. attribute:: data
    
    A dict of processed data. Each key is the name of the dataset and each value is a reference to the data.
    
    """
   
 
    def __init__(self,event,entries,config=None):
        self.event=event
        self.maps=None
        self.entries=entries
        self.config=config
 
        self.evid=event.eventid
        self.dir='data/' + self.evid
        self.products=[]        
        self.data=[]

        with open(config.products['file']) as f:
          self.allProducts=yaml.load(f)

        
    def createAll(self):

        count=0
        for p in self.allProducts:
            count+=self.create(**p)
        return count


    def create(self,name=None,type=None,dataset=None,format=None):
        print('Making:',name,type,dataset,format)

        if dataset:
            data=self.getDataset(dataset)

        # Set working directory 
        os.makedirs(self.dir,exist_ok=True)

        if type=='contents':
            data=Contents(self.dir)

        elif type=='graph':
            data=Graph(name=name,event=self.event,data=dataset)

        elif data:
            pass

        else:
            raise nameError('Cannot create blank product')

        # Now create multiple formats of data
        count=0
        formats=format.split(',') if (',' in format) else [format]
        for format in formats:
            print('format is',format)
            product=Product(dir=self.dir,data=data,name=name,config=self.config).create(format)
            if product:
                self.products.append(product)
                count+=1

        return count
   

    def getDataset(self,name):

        # Reuse precomputed data if possible
        matches=[x for x in self.data if x.name==name]

        if len(matches)>0:
            return matches[0]

        print('Creating dataset',name)

        if 'geo' in name:
           data=self.entries.aggregate(name)

        else:
            raise NameError('Unknown data type '+name)

        self.data.append(data)
        return data

 
    def __repr__(self):
        if len(self.productFiles)<1:
            return 'No products'
       
        text='' 
        for product in self.products:
            text+='Product:['+product.filename+']'
            return text

    
class Product:

    def __init__(self,dir,data,name,filename=None,config=None):
        self.data=data
        self.dir=dir
        self.name=name
        self.config=config
        self.filename=filename
        print(data)


    def create(self,format):
        data=self.data

        if self.filename:
            filename=self.filename
        else:
            filename=self.dir+'/'+self.name+'.'+format

        product=None
        print('Writing:',filename)

        if format=='json':
            if hasattr(data,'toJSON'):            
                product=data.toJSON()
            else:
                product=json.dumps(data)
            with open(filename,'w') as f:
                f.write(product)
               
        elif format=='geojson':
            if hasattr(data,'toGeoJSON'):            
              product=data.toGeoJSON()
            else:
              print(data)
              product=json.dumps(data)
            with open(filename,'w') as f:
                f.write(product)

        elif format=='xml':
            if hasattr(data,'toXML'):            
              product=data.toXML()
            else:
               raise NameError('Cannot save '+self.name+' as format '+format)

        elif format=='png':
            if hasattr(data,'toImage'):            
              product=data.toImage()
            elif 'type' in data and data['type']=='FeatureCollection':
              filename=self.makeGeoJSONImage(filename)
            else:
              raise NameError('Cannot save '+self.name+' as format '+format)

        else:
            raise NameError('Unknown format '+format)

        self.filename=filename
        if product:
            self.product=product
        return self


    def makeGeoJSONImage(self,filename,inputfile=None):

        if not inputfile:
            inputfile=self.dir+'/'+self.name+'.geojson'
        filename=staticMap.createFromGeoJSON(inputfile,filename,config=self.config)
        return filename
