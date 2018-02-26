Product Guide
-------------

This section lists the available DYFI products and formats. 

DYFI products are event-centric. Each product is tied to a specific Event ID.

Dynamic Map Products
====================

Filenames: `dyfi_geo_1km.geojson` and `dyfi_geo_10km.geojson` 

These are text files in GeoJSON format (see http://geojson.org/). These represent a collection of UTM block areas of either 1 km or 10 km size, wherein individual DYFI responses are aggregated (see the :ref:`Scientific Guide` for details.) 

The topmost object of each file is a `FeatureCollection` with the following keys:

===========   =======================================
name          The aggregation size (1km or 10 km)
id            same
type          FeatureCollection
features      array of location Features, see below
properties    see below
===========   =======================================

The `FeatureCollection` properties are:

=========   ================================================================
nresp       The number of individual responses in the dataset for this file
maxint      The largest intensity value among aggregated locations
=========   ================================================================

Each `Feature` in the `FeatureCollection` represents one aggregated location (geocode block). The location's `geometry` attribute is a GeoJSON `Polygon` which maps the four corners of the UTM block.

The `Feature` properties for each location are:

==========  ==============================================================
type        Feature
id          The UTM string for this location
location    Same as ID
nresp       The number of individual responses contributing to this block
intensity   The aggregated intensity computed from these responses
center      A `Point` GeoJSON indicating the center of this block
==========  ==============================================================

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

