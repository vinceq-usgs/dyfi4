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

Data fields
===========

The following fields are supported.


ciim_mapConfidence: a measure the confidence of the geolocation method. 
- Filled in my the web form's geocoding algorithm. 
- Possible values:

- 5 rooftop precision
- 4 neighborhood precision (~100 m)
- 3 block precision (~1 km)
- 2 city precision (~10 km)
- 1 regional precision (~100 km)
- 0 unknown or bad location

eventid
ciim_mapAddress' => 'null',
ciim_mapConfidence' => '4',
ciim_mapLat' => '33.62674894775717',
ciim_mapLon' => '-117.75911424010992',
ciim_time' => 'Mon, 02 Jul 2018 19:03:14 GMT',
eventTime
form_version
language
server
timestamp

 

