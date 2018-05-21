Introduction to Did You Feel It? (DYFI) 
---------------------------------------

|Travis| |CodeCov| |Codacy|

.. |Travis| image:: https://travis-ci.org/vinceq-usgs/dyfi4.svg?branch=core
    :target: https://travis-ci.org/vinceq-usgs/dyfi4
    :alt: Travis Build Status
.. |CodeCov| image:: https://codecov.io/gh/vinceq-usgs/dyfi4/branch/core/graph/badge.svg
    :target: https://codecov.io/gh/vinceq-usgs/dyfi4
    :alt: Code Coverage Status
.. |Codacy| image:: https://api.codacy.com/project/badge/Grade/cc5a3a34ef56478e897414ab5472d5dc    
    :target: https://www.codacy.com/app/vinceq-usgs/dyfi4?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=vinceq-usgs/dyfi4&amp;utm_campaign=Badge_Grade
    :alt: Codacy Grade

`Did You Feel It? (DYFI)` collects information from people who felt an earthquake and creates a map that shows the felt level of shaking in the area around the epicenter.

DYFI was developed to tap the abundant information available about earthquakes from the people who experience them. By taking advantage of the vast number of Internet users, we can get a more complete description of what people experienced, the effects of an earthquake, and the extent of damage. 

This version (Version 4) is written in Python and is under development.

Source code: https://github.com/vinceq-usgs/dyfi4/tree/core

Manual: https://vinceq-usgs.github.io/dyfi4/

INSTALLATION
============

1. Clone this repository. By default, this will install to the directory 'dyfi4'.
    
2. Run the install script by typing:
    
        `cd dyfi4; ./install.sh`
        
Note that miniconda is required for this step. See https://conda.io/miniconda.html to install.

3. (ADVANCED USERS ONLY) If you are using different event and entry datasets from the included DYFI dataset, edit the file 'tests/config.yml' and make sure the 'db' section has the correct information.  

4. Whenever you want to run DYFI, activate the virtual environment by typing:

        `source activate dyfi`

(You may wish to alias this to something shorter, like "dyfi".)

5. To make sure the installation is complete, go to the repo root directory and run 'pytest'.

NEXT STEPS
==========
- queue, incoming equivalents

HISTORY
=======
- V4.01: Rewrite modules for more modularity
- V4.02: Complete coverage for core functions
- V4.03: Remove queue/incoming for now; fork development to 'core'
- V4.rc1: Release Candidate 1



