# -*- coding: utf-8 -*-
"""

A collection of functions to aggregate lists of entries into geocoded boxes or ZIP code locations and compute their aggregated intensities. (*Note*: ZIP codes not yet implemented)

"""

import math
import geojson

from . import cdi
from .thirdparty.utm import from_latlon,to_latlon,OutOfRangeError

PRECISION=4  # Maximum precision of lat/lon coordinates of output

def aggregate(entries,producttype):
    """

    :synopsis: Aggregate entries into geocoded boxes
    :param entries: list of :py:class:`Entry` objects
    :param producttype: The product type (zip, geo_1km, geo_10km)
    :returns: `GeoJSON` :py:obj:`FeatureCollection`

    The return value is a `GeoJSON` :py:obj:`FeatureCollection` with
    the following properties:

    ======  ========================================
    name    Same as :py:obj:`producttype`
    id      Same as :py:obj:`producttype`
    nresp   Total number of responses from each valid location
    maxint  Maximum intensity from each valid location
    ======  ========================================

    Each Feature in the `GeoJSON` FeatureCollection has the attribute:

    ===   =================================================
    id    UTM string or ZIP code of this Feature's location
    ===   =================================================

    and the following properties:

    ==========  ==========================================
    location    same as id
    center      Center of this location, for plotting (GeoJSON Point)
    nresp       number of responses in this location
    intensity   aggregated intensity for this location
    ==========  ==========================================

    """

    aggregator=None

    # producttype is either 'geo_1km', '10km', or 'zip'
    if 'geo' in producttype:
        aggregatetype='geo'
        aggregator=getUtmForEntry

        if '_1km' in producttype or producttype=='1km':
            resolutionMeters=1000

        elif '_10km' in producttype or producttype=='10km':
            resolutionMeters=10000

        else:
            aggregator=None

        """
    elif 'zip' in producttype:
        aggregatetype='zip'
        aggregator=getZipForEntry
        resolutionMeters=0
        """

    if not aggregator:
        raise ValueError('Aggregate: got unknown type '+producttype)

    # Loop through each entry, compute which bin it belongs

    rawresults={}
    npts=len(entries)
    nlocated=0
    for entry in entries:
        location=aggregator(entry,resolutionMeters)

        # location is now either a UTM or ZIP (string)
        # TODO: Filter based on precision of the input coords
        if not location:
            continue

        if location not in rawresults:
            rawresults[location]=[]

        rawresults[location].append(entry)
        nlocated+=1

    print('Aggregate: For %s, %i/%i entries located.' %
      (producttype,nlocated,npts))

    # Now each location has geographic information.
    # Turn this into a GeoJSON object.

    features=[]
    maxcdi=0
    totalresp=0
    for location,entries in rawresults.items():

        geometry=None
        if aggregatetype=='geo':
            geometry=getUtmPolyFromString(location,resolutionMeters)
            """
        elif aggregatetype=='zip':
            geometry=getZipCoordinates(location)
            """

        # Catchall if from_latlon created a valid UTM string
        # from a latlon, but to_latlon could not create a
        # bounding box.
        if not geometry:
            continue # pragma: no cover

        bounds=geometry['bounds'] # type Polygon
        center=geometry['center'] # type Point

        nresp=len(entries)
        totalresp+=nresp

        thiscdi=cdi.calculate(entries)
        if thiscdi>maxcdi:
            maxcdi=thiscdi

        pt=geojson.Feature(
            id=location,
            geometry=bounds,
            properties={
                'location':location,
                'nresp':nresp,
                'center':center,
                'intensity':thiscdi
            }
        )
        features.append(pt)

    featurecollection=geojson.FeatureCollection(
        id=producttype,
        features=features,
        properties={
            'nresp':totalresp,
            'maxint':maxcdi
        }
    )

    featurecollection.name=producttype
    print('Aggregate: %i pts into %i locations, maxint=%i' %
          (npts,len(features),maxcdi))
    return featurecollection


#---------------------
# UTM Helper Functions
#---------------------

def getUtmFromCoordinates(lat,lon,span=None):
    """

    :synopsis: Convert lat/lon coordinates to UTM string
    :param float lat: Latitude
    :param float lon: Longitude
    :param span: (optional) Size of the UTM box (see below)
    :returns: UTM string with the correct resolution

    Convert lat/lon coordinates into a UTM string using the :py:obj:`UTM` package. If :py:obj:`span` is specified, the output is degraded via the :py:obj:`floor` function.

    :py:obj:`span` accepts the values 'geo_10km', 'geo_1km', or the size of the UTM box in meters (should be a power of 10).

    This will NOT filter the location based on precision of the input coordinates.

    """

    if span=='geo_1km' or span=='1km' or span==1000:
        span=1000
    elif span=='geo_10km' or span=='10km' or span==10000:
        span=10000
    else:
        raise TypeError('Invalid span value '+str(span))

    try:
        loc=from_latlon(lat,lon)
    except OutOfRangeError:
        return

    x,y,zonenum,zoneletter=loc
    if span:
        x=myFloor(x,span)
        y=myFloor(y,span)

    utm='{} {} {} {}'.format(x,y,zonenum,zoneletter)
    return utm


def getUtmForEntry(entry,span):
    """

    :synopsis: Find the UTM location for an entry
    :param entry: The :py:obj:`Entry` object to locate
    :param span: Size of the UTM box (see below)
    :returns: UTM string with the correct resolution

    Compute the UTM block for an :py:obj:`Entry` object using :py:func:`getUtmFromCoordinates`. The UTM coordinate resolution is degraded via the :py:obj:`floor` function depending on the :py:obj:`span` parameter.

    :py:obj:`span` accepts the values 'geo_10km', 'geo_1km', or the size of the UTM box in meters (should be a power of 10).

    """

    try:
        lat=float(entry.latitude)
        lon=float(entry.longitude)
    except TypeError:
        return

    loc=getUtmFromCoordinates(lat,lon,span)
    return loc


def getUtmPolyFromString(utm,span):
    """

    :synopsis: Compute the (lat/lon) bounds and center from a UTM string
    :param utm: A UTM string
    :param int span: The size of the UTM box in meters
    :return: dict

    Get the bounding box and center point for a UTM string suitable for plotting.

    The return value has two keys:

    ======    ========================
    center    A GeoJSON Point object
    bounds    A GeoJSON Polygon object
    ======    ========================

    """

    x,y,zone,zoneletter=utm.split()
    x=int(x)
    y=int(y)
    zone=int(zone)

    # Compute bounds. Need to reverse-tuple here because the
    # to_latlon function returns lat/lon and geojson requires lon/lat.
    # Rounding needed otherwise lat/lon coordinates are arbitrarily long

    def _reverse(tup):
        (x,y)=tup
        x=round(x,PRECISION)
        y=round(y,PRECISION)
        return (y,x)

    p1=_reverse(to_latlon(x,y,zone,zoneletter))
    p2=_reverse(to_latlon(x,y+span,zone,zoneletter))
    p3=_reverse(to_latlon(x+span,y+span,zone,zoneletter))
    p4=_reverse(to_latlon(x+span,y,zone,zoneletter))
    bounds=geojson.Polygon([[p1,p2,p3,p4,p1]])

    # Compute center
    cx=int(x)+span/2
    cy=int(y)+span/2
    clat,clon=to_latlon(cx,cy,zone,zoneletter)
    clat=round(clat,PRECISION)
    clon=round(clon,PRECISION)
    center=geojson.Point((clon,clat))

    return ({'center':center,'bounds':bounds})


#-------------------------
# Zipcode Helper Functions
#-------------------------

"""
def getZipLocation(entry,resolution):

    :synopsis: Find the ZIP code of an entry.
    :param entry: The :py:obj:`Entry` object to locate
    :param resolution: (ignored)
    :return: The ZIP code (in str format)

    This reads the 'zip' attribute of the Entry object.
    If that is blank, it checks for a :code:`citydb` that has
    the :code:`zip` database.
    If it is, then this returns the :code:`cityid` value.

    Finally, if neither exists, create a 'city' circle instead.


    if entry.zip:
        return entry.zip

    if entry.citydb:
        return '%s:%s' % (entry.citydb,entry.cityid)


def getZipCoordinates(zipcode):

    :synopsis: Get the ZIP polygon and center of a ZIP code or cityid.
    :param zipcode: A UTM string
    :return: dict

    The return value has two keys:

    ======  =========================
    center  A GeoJSON Point object
    bounds  A GeoJSON Polygon object
    ======  =========================


    # TODO: Look up ZIP code or cityid coordinates
    # Disabled for now
    return
"""

#-------------------------
# Utility Functions
#-------------------------

def myFloor(x,multiple):
    """

    :synopsis: Round down to a multiple of 10/100/1000...
    :param float x: A number
    :param int multiple: Power of 10 indicating how many places to round
    :returns: int

    This emulates the `math.floor` function but
    rounding down a positive power of 10 (i.e. 10, 100, 1000...)

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
    rounding up a positive power of 10 (i.e. 10, 100, 1000...)

    For example, myCeil(1975,100) returns 2000.

    """

    return int(math.ceil(x/multiple) * multiple)

