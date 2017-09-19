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
    
    :synopsis: Handle product generation for an event. This calls other product generators like :py:obj:`Contents` and :py:obj:`Map`.
    :param event: :py:obj:`Event` object
   
    TODO

    """
 
    def __init__(self,event,entries,config):
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
            created=self.create(p)
            if created:
                count+=created
                
        return count


    # Create a particular Product object using the parameters in p
    # This will compute the data specified in p['dataset'], if necessary
    # Creating a Product object also creates the thing specified by 'format'

    def create(self,p):

        name=p['name'] if 'name' in p else None
        dataType=p['type'] if 'type' in p else None
        dataset=p['dataset'] if 'dataset' in p else None

        count=0
        if 'format' not in p:
            return count

        format=p['format']
        product=Product(self,**p)

        if product:
            self.products.append(product)
            count+=1
        else:
            print('Products.create: Oops, did not create.')
     
        return count
   

    def getDataset(self,dataType):

        print('Products.getDataset: Getting',dataType)
        # Reuse precomputed data if possible

        matches=[x for x in self.data if 
            (hasattr(x,'name') and x.name==dataType) or
            ('name' in x and x['name']==dataType)]
        if len(matches):
            return matches[0]

        if 'geo_' in dataType:
            data=self.entries.aggregate(dataType)

        elif 'time' in dataType:
            data=self.entries.getTimes(dataType)

        else:
            raise NameError('Unknown data type '+dataType)

        self.data.append(data)
        return data

 
    def __repr__(self):
        text='Products:[' 
       
        if len(self.productFiles)<1:
            return text+']'
     
        names=[]
        for product in self.products:
            names.append('Product:['+product.name+']')

        return text+','.join(names)+']'
   

class Product:

    def __init__(self,parent,name,dataset=None,type=None,format=None):

        print('Product: initializing',name)
        self.parent=parent
        self.dir=parent.dir

        self.name=name
        self.config=parent.config
        self.data=None
       
        if dataset:
            self.data=parent.getDataset(dataset)

        func=None
        if type=='graph':
            func=Graph
        elif type=='map':
            func=Map
        elif type=='contents':
            self.data=Contents(event=parent.event,dir=self.dir)

        if func:
            self.data=func(name=name,event=parent.event,data=self.data,config=self.config,dir=self.dir)

        if format:
            self.create(format)


    def create(self,format,filename=None):

        name=self.name
        if not filename:
            filename='%s/%s.%s' % (self.dir,name,format)

        self.filename=filename

        data=self.data
        product=None

        if format=='json':
            if hasattr(data,'toJSON'):            
                product=data.toJSON()
            else:
                product=json.dumps(data)
               
        elif format=='geojson':
            if hasattr(data,'toGeoJSON'):            
                product=data.toGeoJSON()
            else:
              product=json.dumps(data)

        elif format=='xml':
            if hasattr(data,'toXML'):            
                product=data.toXML()

        elif format=='png':
            if hasattr(data,'toImage'):
                product=data.toImage()

        if not product:
            raise NameError('Cannot save '+self.name+' as format '+format)

        if isinstance(product,str):
            with open(filename,'w') as f:
                f.write(product)

        self.filename=filename
        if product:
            self.product=product
        return self

