Product Guide
-------------

This section lists the available DYFI products and formats. 

DYFI products are event-centric. Each product is tied to a specific Event ID.

Dynamic Map Products
====================

Filenames: `dyfi_geo_1km.geojson` and `dyfi_geo_10km.geojson` 

These are text files in GeoJSON format (see http://geojson.org/). Each file is a GeoJSON `FeatureCollection` where each `Feature` represents a UTM block area of either 1km or 10km size. This makes it easy to compare intensities at the same locations for different events.

Each `Feature` in the `FeatureCollection` represents one aggregated location (geocode block). For more information see :ref:`Aggregation`. 

Each `Feature` containts the following properties:

==========  ==============================================================
type        **Feature**
id          The UTM string for this location
location    Same as *id*
nresp       The number of individual responses contributing to this block
intensity   The aggregated intensity computed from these responses
center      A GeoJSON `Point` object indicating the center of this block
==========  ==============================================================

In addition, the `FeatureCollection` object has its own keys and properties:

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

We consider the GeoJSON products to be the "standard" DYFI product from which other products (static maps and graphs) are derived.

Static Map Products
===================

JPEG
....

Filenames: `dyfi_geo_1km.png` and `dyfi_geo_10km.png` 

These PNG files are graphical representations of the GeoJSON data. There is one static image for each version of the aggregation (1 km and 10 km). The aggregated blocks are plotted with colors corresponding to intensity; the color scale is the same used by previous versions.

In addition to the GeoJSON, we include the following data on the map legend:

- Event ID
- Event information (magnitude, date/time)
- Maximum intensity
- Number of entries represented in the database (note that some entries might be off-map)
- The basemap from OpenStreetMaps (https://www.openstreetmap.org/)

**New in DYFI Version 4**

While the previous version of DYFI used Generic Mapping Tools (GMT) for static map creation, DYFI now uses `Leaflet` for map generation. See `Creation of static images` for details.

DYFI now has the the ability to plot the intensity data with different levels of transparency, depending on how many entries (not including filtered or suspect entries) which were used in computing the intensity in a particular aggregated block. This provides an intuitive sense of where the DYFI data is most robust (solid colored blocks) and where the intensity is uncertain because there are fewer data points in that location (transparent blocks).

==================  ==========================
Number of entries    Opacity level (1=solid)
------------------  --------------------------
<1                    0.3
10+                   1.0
==================  ==========================

KML
...

Filename: dyfi_combined.kmz

KML (Keyhole Markup Language) is a file format used to display geographic data in an Earth browser such as Google Earth. The *.kmz* extension means that the data has been zipped (compressed). For more information see https://developers.google.com/kml/.

This KML dataset contains three layers:

- epicenter data (latitude/longitude/event time) 
- the 1km aggregated dataset
- the 10km aggregated datast

XML
...

Filename: `contents.xml`

The file `contents.xml` is used only by the USGS Event Pages website to indicate which DYFI products will be available for display and/or download. It includes a full listing of each product along with the available file formats. If you are not exporting to the USGS Event Pages, this file is not necessary.

Graph Products
==============

Note that a static image is no longer provided by DYFI. The USGS Event Pages are expected to take this data and render it on a browser via the :obj:`D3` visualization package.

Instead, the graph data is packaged in a JSON file. Each dataset is stored in a **dataset** array (see details of each file below), along with the title and x and y axis labels for plotting.

Distance vs Intensity Datafile
..............................

Filename: dyfi_plot_atten.json

This file is a summary of the DYFI data in a format suitable for plotting in a graph that compares intensity with distance. The **x** axis in each dataset is **epicentral distance**. The **y** axis is intensity. Data that is deemed suspect of filtered out is not included in these datasets.

The datasets included in this file are:

Aggregated data
++++++++++++++++++

=======  ===============================
class    scatterplot1
data     epicentral distance, intensity
id       scatterdata
legend   Aggregated geo_10km data
=======  ===============================

This dataset is the intensity and **epicentral** distance for each aggregated block. Each datapoint represents one UTM block. The **x** of each datapoint is the epicentral distance computed to the geographical center of the block. The **y** coordinate is the computed intensity for all entries in that block.


Mean of aggregated data
++++++++++++++++++++++++++

======   ===============================
class    mean
data     see below
id       meanBinned
legend   Mean intensity in bin
======   ===============================

For this dataset, the aggregated data is binned together into bins of equal log distance. Each datapoint in this dataset represents a distance bin.  Within each bin, we compute the mean value and standard deviation of the intensities of all aggregated blocks inside the bin. Each point (bin) has the following data:

    =======  =======================================================
    min_x    The minimum distance of this bin
    max_x    The maximum distance of this bin
    x        The log mean distance of this bin (for plotting)
    y        The mean of the intensities of all blocks in this bin
    stdev    The standard deviation of the intensities
    =======  =======================================================

Median of aggregated data
++++++++++++++++++++++++++++

=======  ===============================
class    median
data     see below
id       medianBinned
legend   Median intensity in bin
=======  ===============================

For this dataset, the aggregated data is binned together into bins of equal log distance. Each datapoint in this dataset represents a distance bin.  Within each bin, we compute the median value of the intensities of all aggregated blocks inside the bin. Each point (bin) has the following data:

    =======  =======================================================
    min_x    The minimum distance of this bin
    max_x    The maximum distance of this bin
    x        The log mean distance of this bin (for plotting)
    y        The median of the intensities of all blocks in this bin
    =======  =======================================================


Estimated Intensity 1
+++++++++++++++++++++
=======  ===================================================
class    estimated_1
data     x,y pairs of distance and intensity
id       ipe_aww2014_wna
legend   Atkinson, Worden, Wald 2014 (WNA)
=======  ===================================================

This dataset is used for comparing an IPE (Intensity Prediction Equation) to the actual DYFI data. The IPE used to compute the expected intensity for a typical earthquake of this magnitude, calculated at evenly spaced intervals for plotting.

In this case, the IPE is Atkinson, Worden, Wald 2014 (Western North America). For more on IPEs, see the :obj:`Scientific Guide`.


estimated_2
+++++++++++
=======  ===================================================
class    estimated_2
data     x,y pairs of distance and intensity
id       ipe_aww2014_ena
legend   Atkinson, Worden, Wald 2014 (ENA)
=======  ===================================================

Same as above, except the IPE used is Atkinson, Worden, Wald 2014 (Eastern North America). For more on IPEs, see the :obj:`Scientific Guide`.

Time vs Responses Datafile
..........................

Filename:

