import json
import yaml

from .graph import Graph
from .map import Map

class Products:
    """

    :synopsis: Handle the generation of all the products 
    :param event: A :py:obj:`dyfi.event.Event` object
    :param entries: A :py:obj:`dyfi.entries.Entries` object
    :param config: A :py:obj:`dyfi.config.Config` object

    Create all the output files for an event. Each product is held in a :py:class:`dyfi.products.Product` object, which also runs the required product generation methods.

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
          self.allProducts=yaml.safe_load(f)


    def createAll(self):
        """

        :synopsis: Loop through all product types and create them
        :returns: how many products were created

        The list of products and parameters in the :file:`product.yml` are used as parameters for the :py:meth:`create` method.

        """

        count=0
        for p in self.allProducts:
            created=self.create(p)
            if created:
                count+=created

        return count


    def create(self,p):
        """

        :synopsis: Create a :py:class:`Product` object and underlying thing
        :param dict p: Set of parameters
        :returns: Number of products created

        Create a particular Product using the parameters in `p`. The following parameter keys are accepted in `p` (and are found in :file:`products.yml`):

        - name
        - dataset (geo_1km, geo_10km, time)
        - format (geojson, png, json)
        - type (map or graph)

        If the `dataset` parameter is specified (e.g. 'geo' or 'time'), that dataset will be computed. 

        If the 'formatType'  is specified, the :py:class:`Product` initializer will create the product as well (see :py:meth:`Product.create`).

        """

        count=0
        params=dict()
        for k,v in p.items():
            if k=='type':
                params['productType']=v
            elif k=='format':
                params['productFormat']=v
            else:
                 params[k]=v

        if 'productFormat' not in params:
            return count

        product=Product(self,**params)

        if product:
            self.products.append(product)
            count+=1

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
            raise NameError('Unknown datatype '+dataType)

        self.data.append(data)
        return data


    def __repr__(self):
        text='Products:['

        if len(self.products)<1:
            return text+']'

        names=[]
        for product in self.products:
            names.append('Product:['+product.name+']')

        return text+','.join(names)+']'


class Product:
    """

    :synopsis: Handle the generation of a single product
    :param parent: A :py:obj:`Products` object
    :param str name: The name of this product
    :param dataset: See below
    :param productType: See below
    :param productFormat: See below

    Holds the output for particular product. This calls other product generators like :py:obj:`Contents` and :py:obj:`Map`.

    If the `dataSet` parameter is set, this will run whatever method is needed to process the raw data (for example, geocoded aggregation, or generating time series data.)

    If the `productType` parameter is set, this will create a :py:obj:`dyfi.graph.Graph` or :py:obj:`dyfi.map.Map` object from the processed data.

    If the `productFormat` parameter is set, this will run the appropriate `create()` method to make and save the file.

    """

    def __init__(self,parent,name,dataset=None,productType=None,productFormat=None):

        print('Product: initializing',name)
        self.parent=parent
        self.dir=parent.dir

        self.name=name
        self.config=parent.config
        self.data=None

        if dataset:
            self.data=parent.getDataset(dataset)

        func=None
        if productType=='graph':
            func=Graph
        elif productType=='map':
            func=Map

        if func:
            self.data=func(name=name,event=parent.event,data=self.data,config=self.config,eventDir=self.dir)

        if productFormat:
            self.create(productFormat)


    def create(self,productFormat,filename=None):
        """

        :synopis:

        """

        name=self.name
        if not filename:
            filename='%s/%s.%s' % (self.dir,name,productFormat)

        self.filename=filename

        data=self.data
        product=None

        if productFormat=='json' or productFormat=='geojson':
            if hasattr(data,'toJSON'):
                product=data.toJSON()
            elif hasattr(data,'toGeoJSON'):
                product=data.toGeoJSON()
            else:
                product=json.dumps(data)

        elif productFormat=='png':
            if hasattr(data,'toImage'):
                data.toImage()
                product='FILE'

        if not product:
            raise NameError('Cannot save '+self.name+' as format '+productFormat)

        if isinstance(product,str) and product!='FILE':
            with open(filename,'w') as f:
                f.write(product)

        self.filename=filename
        if product:
            self.product=product
        return self

