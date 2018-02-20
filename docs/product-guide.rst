Product Guide
-------------

This section lists the available DYFI products and formats. 

DYFI products are event-centric. Each product is tied to a specific Event ID.

Dynamic Map Products
====================

The files `dyfi_geo_1km.geojson` and `dyfi_geo_10km.geojson` are text files in GeoJSON format (see http://geojson.org/). These represent a collection of UTM block areas of either 1 km or 10 km size, wherein individual DYFI responses are aggregated (see the :ref:`Scientific Guide` for details.) 

Each file represents a GeoJSON file. FeatureCollection. The topmost object is a FeatureCollection keys:

-----------------------------------------------
name        The aggregation size (1km or 10 km)
id          same
type        FeatureCollection
features    array of Features (see below)
properties  see below
-----------------------------------------------

The FeatureCollection also has the following properties:

-----------------------------------------------------------------------------
nresp       The number of individual responses in the dataset for this file
maxint      The largest intensity value among aggregated areas
-----------------------------------------------------------------------------

Each feature in the FeatureCollection is one aggregated location.

Static Map Products
===================

JPEG
----

KML
---

GeoJSON
--------

XML
---

The file `contents.xml` is used only by the USGS Event Pages website to indicate which DYFI products will be available for download. It includes a full listing of each product along with the available file formats. If you are not exporting to the Event Pages, this file is not necessary.

Graph Products
==============

- Distance vs Intensity Graph
- Time vs Responses Graph

