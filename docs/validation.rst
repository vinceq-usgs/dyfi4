Validation
==========

.. testsetup::

     from dyfi import cdi
     from entry import Entry

Here we show a series of validation tests to show results consistent with
the algorithm as shown here:

    USGS “Did You Feel It?” Internet-based macroseismic intensity maps.
    David Jay Wald, Vincent Quitoriano, Charles Bruce Worden, Margaret Hopper, James W. Dewey.
    ANNALS OF GEOPHYSICS, 54, 6, 2011; doi: 10.4401/ag-5354

To calculate a DYFI intensity, we first assign numerical values to individual answers to each question in the questionnaire. For each "community" (i.e., geocoded block), the numerical values assigned to each questionnaire are averaged. A weighted sum of the community values for each question, the "Community Weighted Sum", is then computed based on the following equation::

      CWS = 5 x "felt" (0-1)
          + 1 x "motion" (0-5)
          + 1 x "reaction" (0-5)
          + 2 x "stand" (0-1)
          + 5 x "shelf" (0-3)
          + 2 x "picture" (0-1)
          + 3 x "furniture" (0-1)
          + 5 x "damage" (0-3)

      Numbers in parentheses are the range of possible values for that index.

The intensity is then computed as::

      Intensity = |ln|(cws) * 3.3996 - 4.3781

.. |ln| replace:: log\ :sub:`e`

Test 1. Single entry
---------------------------

An entry composed of a single 'I felt it' response, which results in a CWS of 5. 

     >>> entry=Entry({'felt':1})
     >>> cdi.calculate(entry,cwsOnly=True)
     5.0

For any 'felt' response, the minimum intensity is 2 (which corresponds to 'felt' on the MMI intensity scale).

     >>> cdi.calculate(entry)
     2


Test 2. Multiple indices
-----------------------------

Entries with multiple questions answered, resulting in a higher intensity.

    >>> entry=Entry({'felt':1,'motion':2,'reaction':1})
    >>> cdi.calculate(entry,cwsOnly=True)
    8.0
    >>> cdi.calculate(entry)
    2.7

    >>> entry=Entry({'felt':1,'motion':3,'reaction':3,'stand':1,'shelf':1})
    >>> cdi.calculate(entry,cwsOnly=True)
    18.0
    >>> cdi.calculate(entry)
    5.4

    >>> entry=Entry({'felt':1,'motion':5,'reaction':5,'stand':1,'shelf':3,'picture':1,'furniture':1})
    >>> cdi.calculate(entry,cwsOnly=True)
    37.0
    >>> cdi.calculate(entry)
    7.9


Test 3. The 'felt' and 'other_felt' indices
---------------------------------------------

The questionnaire asks the user, "Did you feel the earthquake?" which populates the 'felt' index. We also ask a second question, "Did others feel the earthquake?" This modifies the value of the 'felt' index to produce partial 'felt' values.

The 'other_felt' index corresponds to the following values:

	===================   =========================  ===============
	'other_felt' value    label                      'felt' value
	===================   =========================  ===============
	null                  Not specified              not changed
	2                     No others felt it          0 or 0.36 
	3                     Some felt it               0.72
	4                     Most felt it               1
	5                     Everyone/almost everyone   1
	===================   =========================  ===============

If the user indicates that neither they nor others felt anything, then the 'felt' index is 0.

    >>> cdi.getFeltFromOther(Entry({'felt':0,'other_felt':0}))
    0

If the user indicates that they felt the earthquake (felt index = 1) but no others felt it (other_felt = 2), the 'felt' index is changed to 0.36.

    >>> cdi.getFeltFromOther(Entry({'felt':1,'other_felt':2}))
    0.36

'other_felt' values of 3 and higher overwrite the 'felt' value.

    >>> cdi.getFeltFromOther(Entry({'felt':0,'other_felt':3}))
    0.72
    >>> cdi.getFeltFromOther(Entry({'felt':0,'other_felt':4}))
    1
    >>> cdi.getFeltFromOther(Entry({'felt':0,'other_felt':5}))
    1

Test 4. The 'damage' index
-------------------------------

The 'damage' index is populated by the user ticking on any number of boxes that indicate the damage they observe.  The following tests show the text string and damage value corresponding to each of the possible checkboxes on the questionnaire.

    No damage:
    
    >>> cdi.getDamageFromText('_none')
    0

    Hairline cracks in walls:

    >>> cdi.getDamageFromText('_crackmin')
    0.5

    A few large cracks in walls:

    >>> cdi.getDamageFromText('_crackwallfew')
    0.75

    Many large cracks in walls:

    >>> cdi.getDamageFromText('_crackwallmany')
    1

    Ceiling tiles or lighting fixtures fell:

    >>> cdi.getDamageFromText('_tilesfell')
    1

    Cracks in chimney:

    >>> cdi.getDamageFromText('_crackchim')
    1

    One or several cracked windows:

    >>> cdi.getDamageFromText('_crackwindows')
    0.5

    Many windows cracked or some broken out:

    >>> cdi.getDamageFromText('_brokenwindows')
    2

    Masonry fell from block or brick wall(s):

    >>> cdi.getDamageFromText('_masonryfell')
    2

    Old chimney, major damage or fell down:

    >>> cdi.getDamageFromText('_majoroldchim')
    2

    Modern chimney, major damage or fell down:

    >>> cdi.getDamageFromText('_majormodernchim')
    3

    Outside wall(s) tilted over or collapsed completely:

    >>> cdi.getDamageFromText('_tiltedwall')
    3

    Separation of porch, balcony, or other addition from building:

    >>> cdi.getDamageFromText('_porch')
    3

    Building permanently shifted over foundation:

    >>> cdi.getDamageFromText('_move')
    3

When multiple damage boxes are checked, the largest corresponding value is used.

    >>> cdi.getDamageFromText('_crackmin _crackwallfew _masonry _porch')
    3        

Test 5. Multiple entries
--------------------------

When multiple entries are aggregated in a single location, the intensity is NOT merely the mean of intensities. Instead, the mean is calculated for each index of the CWS equation, before calculating the intensity.

In this example, the CWS for two entries is calculated separately, and for the aggregate of the two. 


    >>> entry_1=Entry({'felt':1,'motion':0,'reaction':0,'stand':0,'shelf':0})
    >>> entry_2=Entry({'felt':1,'motion':5,'reaction':3,'stand':1,'shelf':1})
    >>> cdi.calculate(entry_1,cwsOnly=True),cdi.calculate(entry_2,cwsOnly=True)
    (5.0, 20.0)
    >>> cdi.calculate([entry_1,entry_2],cwsOnly=True)
    12.5

Now the intensities are calculated separately and for the aggregate. Note that the aggregate intensity is not the mean of the individual entry intensities.

    >>> cdi.calculate(entry_1),cdi.calculate(entry_2)
    (2, 5.8)
    >>> cdi.calculate([entry_1,entry_2])
    4.2


Test 6. Multiple entries with unanswered indices
--------------------------------------------------

When an entry does not have a value for an index (i.e., the user did not answer that particular question on the questionnaire), then that questionnaire is not counted for that particular index.

In the following example, the first entry does not have a 'reaction' value. Therefore, during aggregation, the reaction index only counts the value for the second entry.

    >>> entry_1=Entry({'felt':1})
    >>> entry_2=Entry({'felt':1,'reaction':5})
    >>> cdi.calculate(entry_1,cwsOnly=True)
    5.0
    >>> cdi.calculate(entry_2,cwsOnly=True)
    10.0
    >>> cdi.calculate([entry_1,entry_2],cwsOnly=True)
    10.0


Test 7. Comparison with DYFI Version 3
--------------------------------------------

The following is a comparison of DYFI products from Version 3 (the current live version) and the new Version 4. The test event is the 2016-09-03 M5.8 event near Pawnee, Oklahoma (USGS event ID us10006jxs).

We compare the results of the 10km geocoded datasets, in particular the GeoJSON files. We assume that the latest version of DYFI4 was run to populate the data directory at '[root]/data/us10006jxs'. This test extracts the datafile 'dyfi_geo_10km.geojson' for that event. For comparison, a copy of the equivalent file from DYFI3 is stored at '[root]/tests/data/us10006jxs' (last processed 30-03-2018).

Both DYFI3 and DYFI4 runs are using the same input data with 61,961 raw entries.

    >>> import json
    >>> json_dyfi3=json.load(open('../tests/data/us10006jxs/dyfi_geo_10km.geojson','r'))
    >>> json_dyfi4=json.load(open('../data/us10006jxs/dyfi_geo_10km.geojson','r'))

We parse the raw GeoJSON file for the DYFI4 dataset and extract the intensity at each location (which is indexed by the UTM geolocation string).

    >>> dyfi4intensity={}
    >>> for location in json_dyfi4['features']:
    ...     utmstring=location['properties']['location']
    ...     dyfi4intensity[utmstring]=location['properties']['intensity']
    >>> print('DYFI4 dataset has',len(dyfi4intensity),'locations.')
    DYFI4 dataset has 5204 locations.

We do the same for the DYFI3 dataset.

.. testcode::
    :hide:

    import re
    def dyfi3todyfi4format(string):

        parsed=re.search('UTM:\((\d+)(.) (\d+) (\d+) (\d+)\)',string)
        (zonenum,zoneletter,x,y,span)=parsed.groups()

        x=str(int(x)*int(span))
        y=str(int(y)*int(span))
        utm=' '.join([x,y,zonenum,zoneletter])
        return utm

Note that the old DYFI3 style UTM string is converted to the DYFI4 style string (e.g. '650000 3990000 11 S') so that they can be compared directly.

    >>> dyfi3intensity={}
    >>> for location in json_dyfi3['features']:
    ...     utmstring=location['properties']['name']
    ...     utmstring=dyfi3todyfi4format(utmstring)
    ...     dyfi3intensity[utmstring]=location['properties']['cdi']
    >>> print('DYFI3 dataset has',len(dyfi3intensity),'locations.')
    DYFI3 dataset has 5204 locations.

Now we compare the locations at each dataset and make sure they are the same.

    >>> commonLocations=dyfi3intensity.keys() & dyfi4intensity.keys()
    >>> print('There are',len(commonLocations),'locations in common.')
    There are 5204 locations in common.

Finally we compare the intensities computed at each location and make sure they are the same.

    >>> count=0
    >>> for utm in commonLocations:
    ...     if dyfi3intensity[utm]==dyfi4intensity[utm]:
    ...         count+=1
    >>> print('There are',count,'locations with the same intensity.')
    There are 5204 locations with the same intensity.

