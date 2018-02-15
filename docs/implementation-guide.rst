Implementation Guide
====================

The implementation of DYFI Version 4 features a number of changes from previous versions to bring it up-to-date with modern programming standards: 

- Development is now in Github, an open-source repository. 

- The codebase now uses Python in line with coding standards of other USGS earthquake products. 

- Graphics rendering has moved from Generic Mapping Tools (GMT) to Leaflet rendering for map products, and D3 for graph products.

- The database is now implemented in Sqlite3 for its lighter resource footprint.

Installation
------------

DYFI installation should be straightforward. Miniconda (https://conda.io) is the preferred package and environment manager. The install script (install.sh) should install these modules automatically.

Python modules:

==========  =======  =============================================
geojson     1.3.3+   For output products
pyyaml               For configuration files
numpy       1.11.2   Numerical manipulation in :py:obj:`graph.py`
geopy       1.11.0+  Use great_circle for filtering and graphing
apng                 For :py:obj:`makemovie.py`
defusedxml  0.5.0+   For creating :py:obj:`contents.xml`
codecov              For debugging only
pytest-cov           For debugging only
==========  =======  =============================================

Implementation notes
--------------------

- Triggering of events

- User data: the questionnaire, compatibility

- User data: networks, security, liability

- Output and web pages

- Data exchange

