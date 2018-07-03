import pytest
import shutil

testid='ci37511872'
configfile='tests/testconfig.yml'

import os
import glob

def test_products():
    import copy
    from dyfi import Config,DyfiContainer,Contents,Product,Map,Graph,Products

    shutil.rmtree('data/'+testid,ignore_errors=True)

    config=Config(configfile)
    container=DyfiContainer(testid,configfile=configfile)

    # Test getting contents XML directly
    xmldata=Contents(container).toXML(save=False)
    assert '<?xml' in xmldata

    event=container.event
    entries=container.entries
    products=container.products

    assert 'Products:[' in str(products)

    # Test product with no format
    assert Product(products,name='test',dataset='time')

    with pytest.raises(RuntimeError) as exception:
        Product(products,name='blank',dataset='bad')
    assert 'Unknown datatype' in str(exception.value)

    with pytest.raises(RuntimeError) as exception:
        Product(products,name='test',productFormat='bad')
    assert 'Cannot save' in str(exception.value)

    # Test Map blank directory, GeoJSON output
    products.dir=None
    product=Product(products,name='testmap',dataset='geo_10km',productType='map')
    product.create('geojson','tests/testProduct.geojson')
    myMap=product.data
    assert type(myMap).__name__=='Map'

    # Test Map without directory
    data=myMap.data
    myMap=Map('test_geo_10km',event,data,config)
    assert myMap.toGeoJSON(filename='tests/testMap.geojson')

    badconfig=copy.deepcopy(config)
    badconfig.executables['screenshot']=['badexec']
    with pytest.raises(RuntimeError) as exception:
        Map.GeoJSONtoImage('tests/testMap.geojson','tests/testMap.png',badconfig)
    assert 'subprocess call' in str(exception.value)
    # Clean up leftover temp file in leaflet directory
    for fn in glob.glob('leaflet/tmp*.js'):
        os.remove(fn)
    assert len(glob.glob('leaflet/tmp*.js'))==0

    # Test blank product
    assert products.create({})==0

    # Test graph functions

    with pytest.raises(RuntimeError) as exception:
        graph=Graph('badtype',event=event,data=None,config=config)
    assert 'Graph got unknown graph type' in str(exception.value)

    # Test when redoing graph data
    data=entries.aggregate('geo_10km')
    graph=Graph('plot_atten',event=event,data=data,config=config,eventDir='test')
    graph.getScatterData()
    graph.getDistBins()
    assert 'data' in graph.toJSON()

    # Test alternate getScatterData settings
    data=entries.aggregate('geo_1km')
    graph=Graph('plot_atten',event=event,data=data,config=config,eventDir='test')
    scatterdata=graph.getScatterData()
    assert '1 km' in scatterdata['legend']

    data.id='Alternate aggregation'
    graph=Graph('plot_atten',event=event,data=data,config=config,eventDir='test')
    scatterdata=graph.getScatterData()
    assert scatterdata['legend']=='User entries'


    # Test time graph

    data=entries.getTimes('plot_numresp')
    graph=Graph('plot_numresp',event=event,data=data,config=config,eventDir='test')

    # Test no time data

    data['data']=[]
    graph=Graph('plot_numresp',event=event,data=data,config=config,eventDir='test')
    assert graph.data['preferred_unit']=='minutes'

    # Test blank Products
    blankproducts=Products(event=event,entries=entries,config=config)
    assert repr(blankproducts)=='Products:[]'

