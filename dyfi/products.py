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
        type=p['type'] if 'type' in p else None
        dataset=p['dataset'] if 'dataset' in p else None

        if type=='contents':
            return 0

        count=0
        if 'format' not in p:
            return count

        format=p['format']
        print('Products.create: Creating',format)
        product=Product(self,**p)

        if product:
            self.products.append(product)
            count+=1
        else:
            print('Products.create: Oops, did not create.')
     
        return count
   

    def getDataset(self,name):

        # Reuse precomputed data if possible

        matches=[x for x in self.data if x.name==name]
        if len(matches):
            return matches[0]

        if 'geo_' in name:
            print('Products.getDataset:',name)
            data=self.entries.aggregate(name)

        elif 'time' in name:
            print('Products.getDataset:',name)
            data=self.entries.getTimes(name)

        else:
            raise NameError('Unknown data type '+name)

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

        if func:
            print('Product: running object',func.__name__)
            self.data=func(name=name,event=parent.event,data=self.data,config=self.config,dir=self.dir)

        if format:
            print('Product: creating',name,', format',format)
            self.create(format)


    def create(self,format,filename=None):

        name=self.name
        if not filename:
            filename='%s/%s.%s' % (self.dir,name,format)

        self.filename=filename
        print('Product.create: format',format,'filename:',filename)

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

