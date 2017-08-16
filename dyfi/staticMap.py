"""

staticMap
=============

"""

import shutil
import tempfile
import os
import subprocess
import time

def createFromEvent(event):

  """
  :synopsis: Create static image maps from Event object
  :param event: Event object
  :returns: none

  """

  # Create temporary GeoJSON file from Event object

  geometry=Point((event.lon,event.lat))
  props=event.toGeoJSON().properties

  eventGeoJSON = Feature(geometry=geometry)
  for key,val in event.toGeoJSON().properties.items():  
    eventGeoJSON['properties'][key]=val 

  # Copy geocoded GeoJSON

  # Create data.js file and run Chrome

  # Save output


def createFromGeoJSON(inputfile,outputfile,config,verbose=False):

  """
  :synopsis: Create static image map from Event object
  :param inputfile: Input GeoJSON file
  :param outputfile: Output .png file
  :returns: none

  """

  if isinstance(config,str):
    from .config import Config
    config=Config(config)
 
  leafletdir=config.directories['leaflet'] 
  leafletdatafile='%s/data.js' % leafletdir
  pngfile='%s/screenshot.png' % leafletdir

  # This creates a data.js file in the leaflet directory which is just
  # a GeoJSON file but with VAR= to make it valid JavaScript.
  # This is a lot easier than dealing with browser CORS shenanigans.

  tmpfilename=None
  with tempfile.NamedTemporaryFile(mode='w',prefix='tmp.staticMap.',suffix='.js',dir=leafletdir,delete=False) as tmp:
    if verbose:
      print('Created tmpfile',tmp.name)

    tmpfilename=tmp.name
    input=open(inputfile,'r')
    tmp.write('data='+input.read()+';\n')
    if verbose:
      print('Reading inputfile',inputfile)

  if not tmpfilename:
    return

  shutil.move(tmpfilename,leafletdatafile)
  if verbose:
    print('Moving to',leafletdatafile)
  command=config.executables['screenshot']
  command=[line.replace('__ABSPATH__',os.path.abspath(leafletdir))
    for line in command]

  if verbose:
    print('Command:')
    print(' '.join(command))

  if os.path.isfile(pngfile):
    os.remove(pngfile)

  try:
    print(' '.join(command))
    with open('leaflet/tmp.stdout.txt','wb') as out, \
      open('leaflet/tmp.stderr.txt','wb') as err:
      print('Running subprocess')
      subprocess.call(command,cwd=leafletdir,stdout=out,stderr=err,timeout=10)
      print('Done running subprocess')

    shutil.copyfile(pngfile,outputfile)
    if verbose:
      print('Copied to',outputfile)
    return outputfile

  except:
    return

