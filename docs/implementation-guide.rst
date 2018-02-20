Implementation Guide
====================

The implementation of DYFI Version 4 features a number of changes from previous versions to bring it up-to-date with modern programming standards: 

- Development is now in Github, an open-source repository. 

- The codebase now uses Python in line with coding standards of other USGS earthquake products. 

- Graphics rendering has moved from Generic Mapping Tools (GMT) to Leaflet rendering for map products, and D3 for graph products.

- The database is now implemented in Sqlite3 for its lighter resource footprint.

Installation
------------

DYFI installation should be straightforward. Miniconda (https://conda.io) is the preferred package and environment manager. All required packages can be installed using conda (either its own packages or via `pip`). The install script (`install.sh`) should install these packages automatically.

The file `environment.yml` file lists the DYFI dependencies.

Python modules:

==========  =======  =============================================
apng                 For :py:obj:`makemovie.py`
codecov              For debugging only
defusedxml  0.5.0+   For creating :py:obj:`contents.xml`
geopy       1.11.0+  Use great_circle for filtering and graphing
geojson     1.3.3+   For output products
numpy       1.11.2   Numerical manipulation in :py:obj:`graph.py`
pytest               For debugging only
pytest-cov           For debugging only
pyyaml               For configuration files
sqlite               Implements the DYFI database
==========  =======  =============================================

Additional dependencies
-----------------------

- PhantomJS <http://phantomjs.org/) renders maps into static images (PNG). This is installed from `conda` via the `install.sh` script.

- Leaflet (http://leafletjs.com) is used to render maps from GeoJSON-formatted data. DYFI installs Leaflet locally in the `leaflet/inc` directory. You can update those Leaflet components manually or use a CDN for the latest version (see the commented portion of the `leaflet/viewer.html` file for an example of invoking Leaflet via CDN.)

- utm (https://pypi.python.org/pypi/utm) is a Python package for converting latitude/longitude coordinates into UTM (Universal Transverse Mercator) strings. DYFI includes a local version of this module in the directory `dyfi/thirdparty/utm`.

The DYFI database
-----------------

Describe Sqlite3

Generation of map products
--------------------------

DYFI uses Leaflet to turn intensity data into dynamic map products. 


Creation of static images
-------------------------

DYFI uses PhantomJS to turn Leaflet-based maps into static images.

USGS Event Page integration
---------------------------

The following topics are beyond the scope the core functionality and are described elsewhere.


- Event triggering

- Implementation of the questionnaire

- Transfer of user data to the backend servers

- Product distribution: PDL, Event Pages

