Introduction to Did You Feel It? (DYFI) 
---------------------------------------

|Travis| |CodeCov| |Codacy|

.. |Travis| image:: https://travis-ci.org/vinceq-usgs/dyfi4.svg?branch=master
    :target: https://travis-ci.org/vinceq-usgs/dyfi4
    :alt: Travis Build Status
.. |CodeCov| image:: https://codecov.io/gh/vinceq-usgs/dyfi4/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/vinceq-usgs/dyfi4
    :alt: Code Coverage Status
.. |Codacy| image:: https://api.codacy.com/project/badge/Grade/cc5a3a34ef56478e897414ab5472d5dc    
    :target: https://www.codacy.com/app/vinceq-usgs/dyfi4?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=vinceq-usgs/dyfi4&amp;utm_campaign=Badge_Grade
    :alt: Codacy Grade

`Did You Feel It? (DYFI)` collects information from people who felt an earthquake and creates a map that shows the felt level of shaking in the area around the epicenter.

DYFI was developed to tap the abundant information available about earthquakes from the people who experience them. By taking advantage of the vast number of Internet users, we can get a more complete description of what people experienced, the effects of an earthquake, and the extent of damage. 

This version (Version 4) is written in Python and is under development.

INSTALLATION

    1. Run './install.sh'.

    2. (ADVANCED USERS ONLY) If you are using different event and entry datasets from the included DYFI dataset, edit the file 'tests/config.yml' and make sure the 'db' section has the correct information.  

    3. Whenever you want to run DYFI programs, activate the virtual environment by typing:

        `source activate dyfi`
        (You may wish to alias this to something shorter, like "dyfi".)

    4. To make sure the installation is complete, run 'pytest tests/'.

NEXT STEPS

- queue, incoming equivalents

HISTORY
- V4.01: Rewrite modules for more modularity
- V4.02: Complete coverage for core functions
- V4.03: Remove queue/incoming for now


