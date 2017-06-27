"""

File
====

:synopsis: A collection of utilities for file access and filenames.

.. data:: baseDir

    The path to the DYFI base directory.

.. data:: dataDir

    The path to the directory where event output is stored.

"""

import os.path

# TODO: Put this in a configuration file

baseDir='.'
dataDir=baseDir+'/../data'


def getProductDir(evid):
    """

    :synopsis: Give the data directory for a particular event.
    :param str evid: The event ID

    """

    proddir=dataDir+'/'+evid
    
    if not os.path.isdir(proddir):
        print('getProductDir: Creating product directory',proddir)
        os.makedirs(proddir,exist_ok=True)

    return proddir    
    
    
