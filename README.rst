Introduction to Did You Feel It? (DYFI) 
---------------------------------------

|Travis| |CodeCov|

.. |Travis| image:: https://travis-ci.org/vinceq-usgs/dyfi4.svg?branch=master
    :target: https://travis-ci.org/vinceq-usgs/dyfi4
    :alt: Travis Build Status
.. |CodeCov| image:: https://codecov.io/gh/vinceq-usgs/dyfi4/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/vinceq-usgs/dyfi4
    :alt: Code Coverage Status

`Did You Feel It? (DYFI)` collects information from people who felt an earthquake and creates a map that shows the felt level of shaking in the area around the epicenter.

DYFI was developed to tap the abundant information available about earthquakes from the people who experience them. By taking advantage of the vast number of Internet users, we can get a more complete description of what people experienced, the effects of an earthquake, and the extent of damage. 

This version (Version 2) is written in Python and is under development.

For more information, see the DYFI Manual (included in this repository, or https://gitlab.cr.usgs.gov/vinceq/pydyfi/blob/master/doc/_build/html/index.html)

.. note:: 

    Gitlab has disabled viewing of HTML direct from source. To access this manual:

    1. Build this repository, then point your browser to file:///[repo]/doc/_build/html/index.html. 

    OR

    2. Download the PDF version from this repository: https://gitlab.cr.usgs.gov/vinceq/pydyfi/blob/master/doc/_build/latex/modules.pdf

    OR

    3. Use the Github repository (coming soon).

INSTALLATION

1. Install miniconda2. Take note of where you installed it.

2. Edit the file 'setup_env.sh' and point the MINICONDA_DIR variable to the correct miniconda2 directory.

3. Edit the file 'env_vars.sh' and point the PYTHONPATH variable to this installation.

4. If you are using different event and entry datasets from the included DYFI dataset, edit the file 'tests/config.yml' amd make sure the 'db' section has the correct information.

5. Run:
./setup_env.sh
This will, in addition to installing Python modules, put env_vars.sh
in your miniconda environment so it will set PYTHONPATH whenever you
run step 5.

(You will only need to run steps 1-4 once.)

5. Whenever you want to run DYFI programs, activate the virtual environment by typing:
source activate dyfi
(You may wish to alias this to something shorter, like "dyfigo".)


NEXT STEPS

- Static map: time vs. responses
- queue, incoming equivalents

HISTORY
V4.01: Rewrite modules for more modularity




.. image:: https://api.codacy.com/project/badge/Grade/cc5a3a34ef56478e897414ab5472d5dc
   :alt: Codacy Badge
   :target: https://www.codacy.com/app/vinceq-usgs/dyfi4?utm_source=github.com&utm_medium=referral&utm_content=vinceq-usgs/dyfi4&utm_campaign=badger