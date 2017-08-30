"""

Map
===

"""

import shutil
import tempfile
import os
import subprocess
import json
import copy

class Map:
    """
        :synopsis: Create a static graph
        :param str filename: The filename to create
        :param Event event: An Event object
        :param dict mapparams: A dict of params from a eventMap
        :param dict data: Aggregated data in GeoJSON format

    """

    def __init__(self,products,name,data):
        self.event=products.event
        self.config=products.config
        self.dir=products.dir
        self.name=name

        event=self.event
        data=copy.deepcopy(data)
       
        # Add epicenter data
        epicenter={
            'type':'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates':[event.lon,event.lat]
            },
            'properties': {
                'name':'Epicenter',
                'magnitude':event.mag
            }
        }

        data['features'].append(epicenter)
        self.data=data

    def toGeoJSON(self):
        return json.dumps(self.data)

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


    def toImage(self,inputfile=None,outputfile=None,config=None):

        """
        :synopsis: Create static image map from Event object
        :returns: none
        """

        if isinstance(self,Map):
            if not config:
                config=self.config
            dir=self.dir
            name=self.name

        leafletdir=config.directories['leaflet'] 
        leafletdatafile='%s/data.js' % leafletdir
        pngfile='%s/screenshot.png' % leafletdir
        if not inputfile:
            inputfile='%s/%s.geojson' % (dir,name)
        if not outputfile:
            outputfile='%s/%s.png' % (dir,name)

        if os.path.isfile(pngfile):
            os.remove(pngfile)

        # This creates a data.js file in the leaflet directory which is just
        # a GeoJSON file but with VAR= to make it valid JavaScript.
        # This is a lot easier than dealing with browser CORS shenanigans.

        tmpfilename=None
        with tempfile.NamedTemporaryFile(mode='w',prefix='tmp.Map.',suffix='.js',dir=leafletdir,delete=False) as tmp:
            tmpfilename=tmp.name
            with open(inputfile,'r') as input:
                tmp.write('data='+input.read()+';\n')

        if (not tmpfilename 
            or not os.path.isfile(tmpfilename) 
            or os.path.getsize(tmpfilename)<10):
            return

        shutil.move(tmpfilename,leafletdatafile)
        command=config.executables['screenshot']
        command=[line.replace('__ABSPATH__',os.path.abspath(leafletdir))
            for line in command]

        try:
            print(' '.join(command))
            out=open('leaflet/tmp.stdout.txt','wb')
            err=open('leaflet/tmp.stderr.txt','wb')
            print('Map.toImage: Running subprocess...')
            subprocess.call(command,cwd=leafletdir,stdout=out,stderr=err,timeout=10)
            print('...Done.')

            shutil.copyfile(pngfile,outputfile)
            out.close
            err.close
            return outputfile

        except:
            raise NameError('Something wrong with subprocess call!') 

