"""

Aggregate
=========

:synopsis: A collection of functions to aggregate lists of entries into geocoded boxes or ZIP code locations and compute their aggregated intensities.

"""

import math
import geojson

from . import cdi
from .thirdparty.utm import from_latlon,to_latlon,OutOfRangeError

PRECISION=4  # Maximum precision of lat/lon coordinates of output


def aggregate(entries,producttype):
    """

    :synopsis: aggregate entries into geocoded boxes.
    :param entries: list of :py:obj:`entry` objects
    :param producttype: The product type (zip, geo_1km, geo_10km)
    :type entries: list
    :type str span: Geocoding span (e.g. '1km')

    The return value is a `GeoJSON` FeatureCollection with
    the following properties:
    
    ======  ========================================
    key     value
    ======  ========================================
    span    UTM span
    nresp   Total number of responses included
    maxint  Largest intensity among all locations
    ======  ========================================
    
    Each Feature in the FeatureCollection has the attribute: 
    'id' = [UTM string]
    
    and the following properties:
    
    ==========  ==========================================
    key         value
    ==========  ==========================================
    location    UTM code
    center      GeoJSON Point of the center coordinate
    nresp       number of responses in this location
    intensity   aggregated intensity for this location
    ==========  ==========================================
 
    """
    
    # producttype is either 'geo_1km', '10km', or 'zip'
    
    if 'geo' in producttype:
        aggregatetype='geo'
        aggregator=getUtmLocation
        if '1km' in producttype:
            resolutionMeters=1000

        elif '10km' in producttype:
            resolutionMeters=10000
        else:
            print('Aggregate: ERROR: got unknown type',producttype)
            exit()
            
    elif 'zip' in producttype:
        aggregatetype='zip'
        aggregator=getZipLocation
        resolutionMeters=0
        
    else:
        print('Aggregate: ERROR: got unknown type',producttype)
                    
    npts=len(entries)
    print('Aggregate: Got',npts,'entries, aggregating.')

    # Loop through each entry. For each entry, figure out which bin it belongs
    
    rawresults={}
    ignored=0
    for entry in entries:
        location=aggregator(entry,resolutionMeters)
        
        # location is now either a UTM or ZIP (string)
        # TODO: Filter based on precision of the input coords
        if not location:
            ignored=ignored+1
            continue
        
        if location not in rawresults:
            rawresults[location]=[]
            
        rawresults[location].append(entry)

    # Now each location has geographic information.
    # Turn this into a GeoJSON object.

    features=[]
    maxcdi=0
    for location,entries in rawresults.items():

        # This returns a dict with 'bounds' (type Polygon or Point) 
        # and 'center' (type Point)

        if aggregatetype=='geo':
            geometry=getUtmCoordinatesFromString(location,resolutionMeters)        

        elif aggregatetype=='zip':
            geometry=getZipCoordinates(location)
            
        else:
            continue

        if not geometry:
            continue
            
        props={
            'nresp':len(entries),
            'center':geometry['center']
        }
        pt=geojson.Feature(
            geometry=geometry['bounds'],
            properties=props,
            id=location
        )
        thiscdi=cdi.calculate(entries)
        if thiscdi>maxcdi:
            maxcdi=thiscdi 
         
        pt.properties['intensity']=thiscdi
        features.append(pt)

    featurecollection=geojson.FeatureCollection(
        features=features,id=producttype)

    # TODO: Add featurecollection properties maxIntensity, nresp
    
    print('Aggregate: %i pts into %i locations' %
          (npts,len(features)))
    if ignored:
        print('Aggregate: Ignored %i pts' % ignored)
    print('Aggregate: Max CDI: %s' % maxcdi)

    featurecollection.name=producttype
    return featurecollection


def getUtmLocation(entry,span):
    """
    
    :synopsis: Find the UTM location for an entry.
    :param entry: The :py:obj:`entry` object to locate
    :param str res: 'geo_10km', 'geo_1km', or the size of the UTM box in meters
    :return: UTM string with the correct resolution
    
    This will NOT filter the location based on
    precision of the input coordinates.
    
    """
    
    lat=entry.latitude
    lon=entry.longitude
    
    if isinstance(span,str):
        if span=='geo_10km':
            span=10000
        else:
            span=1000
            
    if not lat or not lon:
        print('Aggregate: WARNING: getUtmLocation: subid',
              entry.subid,'has no lat/lon coordinates')        
        return
    
    try: 
        loc=from_latlon(lat,lon)
    except OutOfRangeError:
        return
    if not loc: 
        return

    x,y,zonenum,zoneletter=loc
    x0=myFloor(x,span)
    y0=myFloor(y,span)
    utm='{} {} {} {}'.format(x0,y0,zonenum,zoneletter)
    return utm


def getUtmCoordinatesFromString(utm,span):
    """
    
    :synopsis: Get the bounding polygon and center from a UTM string.
    :param str utm: A UTM string
    :param str span: The size of the UTM box in meters
    :return: dict
    
    The return value has two keys:

    ======  ========================= 
    key     value
    ======  ========================= 
    center  A GeoJSON Point object
    bounds  A GeoJSON Polygon object
    ======  ========================= 

    """
    
    x,y,zone,zoneletter=utm.split()
    x=int(x)
    y=int(y)
    zone=int(zone)

    # Compute bounds
    
    # Need to reverse-tuple here because to_latlon returns
    # lat/lon and geojson requires lon/lat

    def _sanitize(tup):
        # This function ensures that the output is not so precise
        # that it poses a possible personal identity hazard.
        (x,y)=tup
        x=round(x,PRECISION)
        y=round(y,PRECISION)
        return (y,x)
    
    p1=_sanitize(to_latlon(x,y,zone,zoneletter))
    p2=_sanitize(to_latlon(x,y+span,zone,zoneletter))
    p3=_sanitize(to_latlon(x+span,y+span,zone,zoneletter))
    p4=_sanitize(to_latlon(x+span,y,zone,zoneletter))

    bounds=geojson.Polygon([[p1,p2,p3,p4,p1]])
    
    # Compute center
    
    cx=int(x)+span/2
    cy=int(y)+span/2
    clat,clon=to_latlon(cx,cy,zone,zoneletter)

    clat=round(clat,PRECISION)
    clon=round(clon,PRECISION)

    center=geojson.Point((clon,clat))
    
    return ({'center':center,'bounds':bounds})

    
def getZipLocation(entry,resolution):
    """
    
    :synopsis: Find the ZIP code of an entry.
    :param entry: The :py:obj:`Entry` object to locate
    :param resolution: (ignored)
    :return: The ZIP code (in str format)
    
    This reads the 'zip' attribute of the Entry object.
    If that is blank, it checks for a :code:`citydb` that has 
    the :code:`zip` database.
    If it is, then this returns the :code:`cityid` value.
    
    Finally, if neither exists, create a 'city' circle instead.
    
    """
    
    if entry.zip:
        return entry.zip
    
    if entry.citydb:
        return '%s:%s' % (entry.citydb,entry.cityid)
    
    
def getZipCoordinates(location):
    """
    
    :synopsis: Get the ZIP polygon and center of a ZIP code or cityid.
    :param str utm: A UTM string
    :param str span: The size of the UTM box in meters
    :return: dict
    
    The return value has two keys:

    ======  ========================= 
    key     value
    ======  ========================= 
    center  A GeoJSON Point object
    bounds  A GeoJSON Polygon object
    ======  ========================= 

    """

    # TODO: Look up ZIP code or cityid coordinates
    # Disabled for now
    return
    

#----------------------------------
# Utility functions
#----------------------------------

def myFloor(x,multiple):
    """
    
    :synopsis: Round down to a multiple of 10/100/etc.
    :param float x: A number
    :param int multiple: Power of 10 indicating how many places to round
    :returns: int
    
    This emulates the `math.floor` function but
    rounding down more than 1 (i.e. 10, 100, 1000...)

    For example, myFloor(1975,100) returns 1900.
   
    """
    
    y=x/multiple
    return int(math.floor(y) * multiple)


def myCeil(x,multiple):
    """
    
    :synopsis: Round up to a multiple of 10/100/etc.
    :param float x: A number
    :param int multiple: Power of 10 indicating how many places to round
    :returns: int
    
    This emulates the `math.ceil` function but
    rounding to more than 1 (i.e. 10, 100, 1000...)

    For example, myCeil(1975,100) returns 2000.
    
    """

    return int(math.ceil(x/multiple) * multiple)


#-----------------------------

if __name__=='__main__':
    import argparse

    parser=argparse.ArgumentParser(
        description='Get UTM aggregation from lat/lon pair, or lat/lon from UTM string.')
    parser.add_argument('lat', type=str, 
                        help='latitude OR UTM string')
    parser.add_argument('lon', type=float,nargs='?', 
                        help='longitude')
    parser.add_argument('span', type=str,default='geo_1km',nargs='?', 
                        help='UTM span (default 1km)')
    args=parser.parse_args()

    if ' ' in args.lat:
        print('Parsing '+args.lat+' as UTM string.')
        coords=args.lat.split(' ')
        e=float(coords[0])
        n=float(coords[1])
        zn=int(coords[2])
        latlon=to_latlon(e,n,zn,coords[3])
        print('latlon of this UTM string is:')
        print(latlon)
        exit()

    args.lat=float(args.lat)
    args.lon=float(args.lon)
    if args.lat>90 or args.lat<-90:
        print('Latitude out of bounds (inputs must be lat lon [span])')
        exit()
    
    from modules.entries import Entry
    agg=getUtmLocation(
        Entry({'latitude':args.lat,'longitude':args.lon}),
        args.span)
    
    print('UTM for this lat/lon pair (span:'+args.span+') is:')
    print(agg)


