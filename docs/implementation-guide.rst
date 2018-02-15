Implementation Guide
====================

The implementation of DYFI Version 4 features a number of changes from previous versions to bring it up-to-date with modern programming standards: 

- Development is now in Github, an open-source repository. 

- The codebase now uses Python in line with coding standards of other USGS earthquake products. 

- Graphics rendering has moved from Generic Mapping Tools (GMT) to Leaflet rendering for map products, and D3 for graph products.

- The database is now implemented in Sqlite3 for its lighter resource footprint.

Installation
------------

DYFI installation should be straightforward. Miniconda (https://conda.io) is the preferred package and environment manager. All required packages can be installed using conda (either its own packages or via `pip`). The install script (install.sh) should install these packages automatically.

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

Implementation notes
--------------------

(The topics below are beyond the scope the core functionality and will be described later.)

- Triggering of events

- User data: the questionnaire, compatibility

- User data: networks, security, liability

- Output and web pages

- Data exchange

