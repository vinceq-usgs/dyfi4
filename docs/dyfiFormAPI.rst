DYFI Form Responses API V0.3
****************************

(V0.3 updated 2018-08-03)

The DYFI4 backend accepts response files from the DYFI Questionnaire. Each file represents one user response. The backend supports files containing raw query strings (deprecated) and JSON data. The JSON format is described below.

Filename
========

entry.[server].[eventid].[timestamp].[process_id].json

Note that the filename is flexible. Only the ‘entry’ and ‘.json’ text is checked by the backend. However the naming convention makes it easier for the operator to troubleshoot issues.

[server] should be some indication of the origin of the response (e.g. prod01, prod02, dev01, etc.)
[eventid] should be the assumed event ID associated with this response, or ‘unknown’
[timestamp] and [process_id] are for preventing namespace collisions.

Contents
========

- The file must be a valid JSON file. 
- Key values should be strings, not numeric.
- The DYFI algorithm treats ‘0’ responses differently from null responses. Null responses should be no value or the key will be missing entirely.
- The order of keys does not matter.

Example::

  {
          'ciim_mapAddress' => 'null',
          'ciim_mapConfidence' => '4',
          'ciim_mapLat' => '33.62674894775717',
          'ciim_mapLon' => '-117.75911424010992',
          'ciim_time' => 'Mon, 02 Jul 2018 19:03:14 GMT',
          'd_text' => '_tilesfell _masonryfell',
          'eventTime' => 'Mon, 11 Jan 2016 03:13:52 GMT',
          'eventid' => 'ci37511872',
          'fldEffects_appliances' => '0',
          'fldEffects_doors' => '0',
          'fldEffects_furniture' => '0',
          'fldEffects_pictures' => '0',
          'fldEffects_shelved' => '0',
          'fldEffects_walls' => '0',
          'fldExperience_reaction' => '0',
          'fldExperience_response' => 'no_action',
          'fldExperience_shaking' => '0',
          'fldSituation_felt' => '0',
          'fldSituation_others' => '2',
          'fldSituation_situation' => 'outside',
          'fldSituation_sleep' => 'no',
          'form_version' => '1.5',
          'language' => 'en',
          'server' => '9882eca4186b',
          'timestamp' => '1452511332'
          };

Form-generated fields
=====================

The following fields are pre-filled values or populated by the form. Names in parentheses are the corresponding column names in the DYFI backend database (otherwise, the column name is identical.)

eventid
-------

Filled in by the questionnaire template. If the user accesses the form via an event page, this will have the event ID. Otherwise, it should be 'unknown'.

eventTime (event_time)
-----------------------

Filled in by the questionnaire template. If the user accesses the form via an event page, this will have the event origin time (as a UNIX datetime string). Otherwise, it will be blank.

ciim_mapAddress (street)
--------------------------

If the user geolocates their location via a street address, that data is stored here.

ciim_mapConfidence (confidence)
--------------------------------

A measure the confidence of the geolocation method, computed by the web form's geocoding algorithm. 

Possible values:

- 5 rooftop precision
- 4 neighborhood precision (~100 m)
- 3 block precision (~1 km)
- 2 city precision (~10 km)
- 1 regional precision (~100 km)
- 0 unknown or bad location

ciim_mapLat, ciim_mapLon (latitude, longitude)
-------------------------------------------------

Computed by the web form's geocoding algorithm, or manually entered by the user.

timestamp (time_now)
----------------------

The UNIX time (seconds since epoch) when this response was submitted. This is filled by the response subprocess (the script that handles incoming questionnaire form.)

form_version (version)
------------

The version of the questionnaire online. This is updated only when the source is changed.

language
--------

A code that specifies the language version used for the form. Supported values are 'en' (English) and 'es' (Spanish).

server
------

A unique code that specifies the server that received the submitted form. (The server name should be hashed for security.)

User-entered fields
===================

The following fields are filled in by the user.

.. note::

  If a null value is an option, it will be the default. Null values are treated differently from '0' in the DYFI algorithm.

ciim_time (usertime)
------------------------

Label:
  - Time of earthquake
  
This is a text field filled by the user. However, if this form is associated to a particular event ID, that event's origin time will be used instead.

fldSituation_felt (felt)
-------------------------

Label:
  - Did you feel it?

Possible values:
  - 1 : Yes
  - 0 : No

fldSituation_situation (situation)
------------------------------------

Label:
  - What was your situation during the earthquake?

Possible values:
  - [null] : Not specified
  - inside : Inside a building
  - outside : Outside a building
  - veh_stopped : In a stopped vehicle
  - veh_moving : In a moving vehicle
  - other : Other

fldSituation_sleep (asleep)
----------------------------

Label: 
  - Were you asleep?

Possible values:
  - [null]  : Not specified
  - no : No
  - slept : Slept through it
  - woke : Woke up

fldSituation_others (other_felt)
----------------------------------

Label: 
  - Did others nearby feel it?

Possible values:
  - [null]  : Not specified
  - 2 : No others felt it
  - 3 : Some felt it, most did not
  - 4 : Most felt it
  - 5 : Everyone/almost everyone felt it

fldExperience_shaking (motion)
-------------------------------

Label: 
  - How would you describe the shaking?

Possible values:
  - [null]  : Not specified
  - 0 : Not felt
  - 1 : Weak
  - 2 : Mild
  - 3 : Moderate
  - 4 : Strong
  - 5 : Violent

fldExperience_reaction (reaction)
----------------------------------

Label: 
  - How did you react?

Possible values:
  - [null]  : Not specified
  - 0 : No reaction/not felt
  - 1 : Very little reaction
  - 2 : Excitement
  - 3 : Somewhat frightened
  - 4 : Very frightened
  - 5 : Extremely frightened
  
fldExperience_response (response)
----------------------------------

Label: 
  - How did you respond?

Possible values:
  - [null]  : Not specified
  - no_action : Took no action
  - doorway : Moved to doorway
  - duck : Dropped and covered
  - ran_outside : Ran outside
  - other : Other

fldExperience_stand (stand)
----------------------------

Label: 
  - Was it difficult to stand and/or walk?

Possible values:
  - [null]  : Not specified
  - 0 : No
  - 1 : Yes
  
fldEffects_doors (sway)
------------------------

Label: 
  - Did you notice any swinging of doors or other free-hanging objects?

Possible values:
  - [null]  : Not specified
  - 0 : No
  - 1 slight : Yes, slight swinging
  - 1 violent : Yes, violent swinging

fldEffects_sounds (creak)
--------------------------

Label: 
  - Did you hear creaking or other noises?

Possible values:
  - [null]  : Not specified
  - 0 : No
  - 1 slight : Yes, slight noise
  - 1 loud : Yes, loud noise

fldEffects_shelved (shelf)
----------------------------

Label: 
  - Did objects rattle, topple over, or fall off shelves?

Possible values:
  - [null]  : Not specified
  - 0 : No
  - 0 rattled_slightly : Rattled slightly
  - 0 rattled_loudly : Rattled loudly
  - 1 few_toppled_or_fell : A few toppled or fell off
  - 2 many_toppled_or_fell : Many fell off
  - 3 everything : Nearly everything fell off

fldEffects_pictures (picture)
------------------------------

Label: 
  - Did pictures on walls move or get knocked askew?

Possible values:
  - [null]  : Not specified
  - 0 : No
  - 1 did_not_fall : Yes, but did not fall
  - 1 some_fell : Yes, and some fell

fldEffects_furniture (furniture)
---------------------------------

Label: 
  - Did any furniture or appliances slide, topple over, or become displaced?

Possible values:
  - [null]  : Not specified
  - 0 : No
  - 1 : Yes

fldEffects_appliances (heavy_appliance)
----------------------------------------

Label: 
  - Was a heavy appliance (refrigerator or range) affected?

Possible values:
  - [null]  : Not specified
  - 0 : No
  - fell : Yes, some contents fell out
  - shifted : Yes, shifted by inches
  - shifted_foot : Yes, shifted by a foot or more
  - overturned : Yes, overturned

fldEffects_walls (walls)
-------------------------

Label: 
  - Were free-standing walls or fences damaged?

Possible values:
  - [null]  : Not specified
  - 0 : No
  - cracked : Yes, some were cracked
  - fell_partial : Yes, some partially fell
  - fell_complete : Yes, some fell completely

d_text
------

Label: 
  - Was there any damage to the building?

.. note::

    Multiple answers are possible here. If the user selects more than one, the values are concatenated into one string.

Possible values:
  - _none : No Damage
  - _crackmin : Hairline cracks in walls
  - _crackwallfew : A few large cracks in walls
  - _crackwallmany : Many large cracks in walls
  - _tilesfell : Ceiling tiles or lighting fixtures fell
  - _crackchim : Cracks in chimney
  - _crackwindows : One or several cracked windows
  - _brokenwindows : Many windows cracked or some broken out
  - _masonryfell : Masonry fell from block or brick wall(s)
  - _majoroldchim : Old chimney, major damage or fell down
  - _majormodernchim : Modern chimney, major damage or fell down
  - _tiltedwall : Outside wall(s) tilted over or collapsed completely
  - _porch : Separation of porch, balcony, or other addition from building
  - _move : Building permanently shifted over foundation







 

