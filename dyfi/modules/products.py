"""

Product
=======

"""

import json
import os
from collections import OrderedDict

from . import file as File
from .plotmap import PlotMap
from .plotgraph import PlotGraph
from . import productContents as Contents

class Products:
    """
    
    :synopsis: Handle product generation for an event. This calls other product generators like :py:obj:`Contents` and :py:obj:`PlotMap`.
    :param event: :py:obj:`Event` object
    :param str name: type of product (e.g. 'geo_1km', 'zip')
    
        self.maps=None
        self.rawentries=rawentries
        
        self.evid=event.eventid
        self.productDir=File.getProductDir(self.evid)
        self.products=[]        
        self.data={}

    .. attribute:: evid
    
    The event ID for this product.
    
    .. attribute:: event
    
    A reference to the Event object for this product.

    .. attribute:: maps
    
    A reference to the Maps object which provides custom parameters for this product. (Not yet implemented)

    .. attribute:: rawentries
    
    A reference to the Entries object for this product.

    .. attribute:: productDir
    
    The location for output files (from :py:obj:`getProductDir`).

    .. attribute:: products
    
    The list of product filenames.
    
    .. attribute:: data
    
    A dict of processed data. Each key is the name of the dataset and each value is a reference to the data.
    
    """
    
    # productTypes must be ordered because contents needs to be processed last.
    productTypes=OrderedDict([           
        ('map',{
            'datatypes': ['geo_10km','geo_1km','zip'],
            'formats':['geojson','png']
            }),
        ('graph',{
            'datatypes': ['dist_vs_intensity','time_vs_responses'],
            'formats':['geojson']
            }),
        ('contents',{
            'formats':['xml']
            })
        ])
        
        
    def __init__(self,event,maps,rawentries):
        self.event=event
        # TODO: Use map parameters from DB table
        self.maps=None
        self.rawentries=rawentries
        
        self.evid=event.eventid
        self.productDir=File.getProductDir(self.evid)
        self.products=[]        
        self.data={}

        
    def create(self,ptype=None,dtype=None):

        if not ptype:
            for ptype in self.productTypes:
                self.create(ptype,dtype)
            return

        # At this point, ptype is specified (map, graph, or contents)
    
        productdir=self.productDir
        os.makedirs(productdir,exist_ok=True)
        # TODO: Check that this directory exists

        dtypes=self.productTypes[ptype]
        
        if dtype:
            if dtype in dtypes:
                datatypes=[datatype]
            else:
                print('Products.create: No %s in %s, skipping.' % (dtype,ptype))
        
        if ptype=='map':
            self.createMapProducts(ptype,dtypes)
            
        elif ptype=='graph':
            self.createGraphProducts(ptype,dtypes)
            
        elif ptype=='contents':
            contents=Contents.createXML(self.event,productdir)
            self.loadProduct(contents)
            
        # Add other product types here
        
        else:
            raise NameError('Unknown producttype '+ptype)
        
            
    def createMapProducts(self,producttype,productlist):
        
        """
        
        :synopsis: Create map products.
        :param str producttype: geo_1km, geo_10km, zip
        :return: list of product filenames created
        
        """

        dtypes=productlist['datatypes']
        ftypes=productlist['formats']
        
        for dtype in dtypes:
            
            filename=self.productDir+'/dyfi_'+dtype+'.png'
            print('Products: creating',filename)

            dataset=self.rawentries.aggregate(dtype)

            # TODO: Use map params

            plot=PlotMap(
                event=self.event,
                data=dataset)

            self.addProduct(plot.save(filename))
            self.addProduct(self.saveGeoJSON(dtype,dataset))
   
    
    def createGraphProducts(self,producttype,productlist):
        
        """
        
        :synopsis: Create graph products.
        :param str producttype: geo_1km, geo_10km, zip
        :return: list of product filenames created
        
        """

        dtypes=productlist['datatypes']
        ftypes=productlist['formats']
        
        for dtype in dtypes:
            
            filename=self.productDir+'/dyfi_'+dtype+'.png'
            print('Products: creating',filename)

            if dtype=='dist_vs_intensity':
                print('Using set geo_10km aggregated data for',dtype,'plot.')
                dataset=self.rawentries.aggregate('geo_10km')
                
            elif dtype=='time_vs_responses':
                dataset=self.rawentries
                
            # TODO: Use map params
            plot=PlotGraph(
                event=self.event,
                graphtype=dtype,
                data=dataset)
                                                   
            self.addProduct(plot.save(filename))
            self.addProduct(self.saveGeoJSON(dtype,dataset))
            raise NameError('Processing '+dtype)



            
    def createStaticMaps(self):
        # OBSOLETE
        """
            :synopsis: Create a map using parameters from the mapList database table.
            :return: list of created filenames

        """
        mapparams=self.event.mapList()
        filename=self.filename
        out=[]

        # Ignore zoom and zoomout maps for now.
        # Only use the 'base' parameters.
        
        for maprow in mapparams:
            mapid=maprow.mapid
            if 'base' not in mapid:
                continue
                
            if 'base' not in mapid and 'geo' not in mapid:
                filename='dyfi_%s_%s%s'% (
                    self.productType,mapid,self.productformat)

            filename=self.productDir+'/'+filename
            plot=Plot(filename,self.event,maprow,self.data)
            filename=plot.create()
            out.append(filename)

            # TODO: Do PDF, IMAP products here
            
        return out
      
    
    def saveGeoJSON(self,producttype,dataset):
        """
        
        :synopsis: Create a GeoJSON product file of aggregated data.
        :returns: the product filename created
        
        This will create a GeoJSON file of the data referenced 
        by :py:obj:`data`.
        
        """
        
        filename=self.productDir+'/'+'dyfi_'+producttype+'.geojson'
                
        with open(filename, 'w') as outfile:
            json.dump(dataset,outfile,indent=2)
        
        return filename
    
    
    def addProduct(self,product):
        filename=None
        
        if isinstance(product,list):
            for prod in product:
                self.addProduct(prod)
            return
        
        if isinstance(product,str):
            filename=product
        
        elif hasattr(product,'filename'):
            filename=product.filename

        else:
            raise NameError('Products.addProduct unknown product'+product)

        if filename in self.products:
            print('WARNING: Product',product,'already exists.')
                
        else:
            self.products.append(filename)
            
        return filename
    
    
    def __repr__(self):
        if len(self.productFiles)<1:
            return
        
        for name in self.productFiles:
            text='Product:['+','.join(self.productFiles)+']'
            return text
        
            
