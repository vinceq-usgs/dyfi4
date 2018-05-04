Implementation Guide
====================

The implementation of DYFI Version 4 features a number of changes from previous versions to bring it up-to-date with modern programming standards: 

- Development is now in Github, an open-source repository. 

- The codebase now uses Python in line with coding standards of other USGS earthquake products. 

- Graphics rendering has moved from Generic Mapping Tools (GMT) to Leaflet rendering for map products, and D3 for graph products.

- The database is now implemented in Sqlite3 for its lighter resource footprint.

Installation
------------

DYFI installation should be straightforward. Miniconda (https://conda.io) is the preferred package and environment manager. The included install script (`install.sh`) uses *conda* to install the required packages automatically.

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

- PhantomJS <http://phantomjs.org/) renders maps into static images (PNG). Normally, the :file:`install.sh` script installs this via `conda`.

- Leaflet (http://leafletjs.com) is used to render maps from GeoJSON-formatted data. DYFI installs Leaflet locally in the `leaflet/inc` directory. You can update those Leaflet components manually or use a CDN for the latest version (see the commented portion of the `leaflet/viewer.html` file for an example of invoking Leaflet via CDN.)

- utm (https://pypi.python.org/pypi/utm) is a Python package for converting latitude/longitude coordinates into UTM (Universal Transverse Mercator) strings. DYFI includes a local version of this module in the directory `dyfi/thirdparty/utm`.

Configuration file
------------------

The DYFI4 configuration file :file:`config.yml` is in the YAML file format (http://yaml.org).

Most DYFI4 executables can be called with the --config flag to use another, custom configuration file (for testing, for example.)

The file has five sections:

- *db:* This describes the location and type of the DYFI database (see below).

- *directories:* This has links to the data directories.

  - *data:* This points to the output directories. The DYFI4 products for each event ID are stored here, under its own event ID subdirectory.

  - *leaflet:* This points to the directory where Leaflet processing is done. See :obj:`Generation of map products`.

- *executables:*

- *products:* 

- *filter:* This holds settings for filtering entries (to reject bogus or suspect ones). See :obj:`Filtering of entries`.

The DYFI database
-----------------

The DYFI database is currently implemented as a Sqlite3 database. A sample set of databases is included with installation in */tests/db/*. 

We recommend that the tables be placed in a directory such as */db/*. To change the database location, modify the settings for each database file in :file:`config.yml` file under *db:files*.

Each table is a separate file.

Event table
+++++++++++

==========   ===========================
File         :file:`event.db`
Table name   *event*
==========   ===========================

This table holds data for individual earthquake events; most importantly, event earthquake location and time. Each row corresponds to one event.

This table is normally populated by event information from the USGS Comprehensive Earthquake Catalog, or ComCat (https://earthquake.usgs.gov/data/comcat/). This table holds data information for individual earthquake events. A sample table is included (beginning from 2015). 

The event data is described below. 

=====================  =========================================================================
Column                 Description
---------------------  -------------------------------------------------------------------------
eventid                USGS event ID, usually 10 characters; primary key
mag                    Magnitude
lat                    Epicentral latitude 
lon                    Epicentral longitude
depth                  Hypocentral depth
region                 obsolete
source                 2 letter network code
mainshock              obsolete
loc                    Text description of the location (e.g. "9km ENE of San Simeon, CA") 
nresponses             Number of DYFI responses attached to this event
eventdatetime          Earthquake event time in YYYY-MM-DD HH:MM:SS format
createdtime            Time that this row was last created or updated
newresponses           Number of DYFI responses for this event since the last time this was run
run_flag               obsolete
citydb                 obsolete
zipdb                  obsolete
ciim_version           Incremented whenever :obj:`rundyfi.py` runs
code_version           Current version of DYFI when this event was last run
process_timestamp      Time when :obj:`rundyfi.py` was last run
max_intensity          Maximum computed intensity
sent_email             obsolete
event_version          Event information version (from ComCat) 
orig_id                Original USGS event ID 
eventlocaltime         Event local time (from ComCat)
invisible              see below
good_id                obsolete
=====================  =========================================================================

Notes:

All columns are Sqlite text fields.

The column *newresponses* is updated by the backend whenever a new user response is processed, and is reset to zero whenever the :obj:`rundyfi.py` runs. This is how the backend knows when :obj:`rundyfi.py` should be triggered.

The column *orig_id* is initially the same as *eventid*. This allows the 
first event ID to be archived in case the event ID is manually changed.

The column *invisible* is set to true when an event is no longer valid, and DYFI products are no longer applicable. Examples are bogus, duplicate, or non-authoritative events. These events will not be exported, and responses will not be automatically associated to them. (They may still be run manually.)

Obsolete columns are for compatibility with DYFI3 only. They will be removed in a future release.

Extended tables
+++++++++++++++

==========   ===========================
File         :file:`extended_NNNN.db`
Table name   *extended_NNNN*
==========   ===========================

This table holds data for DYFI felt data. Each row corresponds to one user response. This table is populated from the DYFI Questionnaire (see https://earthquake.usgs.gov/data/dyfi/background.php).

Because of the size of the DYFI response data (2 million+ responses as of 2018), each year of data is stored in a separate file. The files and tables are named :file:`extended_NNNN.db` and *extended_NNNN* where NNNN is the 4 digit year. The earliest provided year is 2003. Events before this are stored in the file :file:`extended_pre.db` in the table *extended_pre*.

Sample extended tables for 2015 and 2016 are included, with personally identifiable information (PII) redacted.

The extended table data is described below. 

=====================  =========================================================================
Column                 Description
---------------------  -------------------------------------------------------------------------
subid                  Integer type unique primary key for each row
eventid                Event ID that this response is associated to
orig_id                Original event ID when response was processed
region                 text
time_now               text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text
suspect                text

The text,orig_id text,suspect text,region text,usertime text,time_now text,latitude text,longitude text,geo_source text,zip text,zip_4 text,city text,admin_region text,country text,street text,name text,email text,phone text,situation text,building text,asleep text,felt text,other_felt text,motion text,duration text,reaction text,response text,stand text,sway text,creak text,shelf text,picture text,furniture text,heavy_appliance text,walls text,slide_1_foot text,d_text text,damage text,building_details text,comments text,user_cdi text,city_latitude text,city_longitude text,city_population text,zip_latitude text,zip_longitude text,location text,tzoffset text,confidence text,version text,citydb text,cityid text

Notes:

All columns are Sqlite text fields unless indicated otherwise.

The column *newresponses* is updated by the backend whenever a new user response is processed, and is reset to zero whenever the :obj:`rundyfi.py` runs. This is how the backend knows when :obj:`rundyfi.py` should be triggered.

The column *orig_id* is initially the same as *eventid*. For responses that were not originally attached to an event ("unassociated entries"), both fields would have the value "unknown". This allows the original data to be archived in case the this entry is associated or manually updated.

The column *invisible* is set to true when an event is no longer valid, and DYFI products are no longer applicable. Examples are bogus, duplicate, or non-authoritative events. These events will not be exported, and responses will not be automatically associated to them. (They may still be run manually.)

Obsolete columns are for compatibility with DYFI3 only. They will be removed in a future release.



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

