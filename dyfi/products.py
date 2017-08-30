"""

Products
========

"""

import json
import os
import yaml

from .graph import Graph
from .contents import Contents
from .map import Map

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
            count+=self.create(p)
        return count


    def create(self,p):
        self.name=p['name']
        self.dataset=p['dataset'] if 'dataset' in p else None
        self.type=p['type'] if 'type' in p else None

        self.data=[]
        if self.dataset:
            self.data=self.getDataset(self.dataset)

        # Now create multiple formats of data
        count=0
        if 'format' not in p:
            return count

        formats=p['format'].split(',')
        
        for format in formats:
            product=Product(self).create(format)
            if product:
                self.products.append(product)
                count+=1

        return count
   

    def getDataset(self,name):

        # Reuse precomputed data if possible
        if self.data:
            matches=[x for x in self.data if x.name==name]
            if len(matches)>0:
                return matches[0]

        print('Creating dataset',name)

        if 'geo_' in name:
            data=self.entries.aggregate(name)
            data=Map(self,name,data)

        elif type=='graph':
            pass

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

    def __init__(self,parent,data=None):
        self.parent=parent

        self.dir=parent.dir
        self.name=parent.name
        self.config=parent.config
        
        if data:
            self.data=data
        elif hasattr(parent,'data'):
            self.data=parent.data


    def create(self,format,filename=None):

        name=self.name
        if not filename:
            filename='%s/%s.%s' % (self.parent.dir,name,format)

        self.filename=filename
        print('Product:create:',filename)

        data=self.data

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
        filename=Map.createFromGeoJSON(inputfile,filename,config=self.config)
        return filename
