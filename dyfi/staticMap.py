"""

staticMap
=============

"""

import shutil
import tempfile
import os
import subprocess

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


def createFromGeoJSON(inputfile,outputfile,config):

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

  with tempfile.NamedTemporaryFile(mode='w',prefix='tmp.staticMap.',suffix='.js',dir=leafletdir) as tmp:
    input=open(inputfile,'r')
    tmp.write('data='+input.read()+';\n')
    shutil.copyfile(tmp.name,leafletdatafile)

  command=config.executables['screenshot']
  command=[line.replace('__ABSPATH__',os.path.abspath(leafletdir))
    for line in command]

  if os.path.isfile(pngfile):
    os.remove(pngfile)

  try:
    subprocess.run(command,cwd=leafletdir)
    shutil.copyfile(pngfile,outputfile)
    return outputfile

  except:
    print('Could not create',pngfile)
    return

