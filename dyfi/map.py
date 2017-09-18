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

    def __init__(self,name,event,data,config,dir=None):

        print('Map: Creating',name,'object.')
        self.name=name
        self.event=event
        self.config=config
        self.dir=dir

        if not dir:
            self.dir='data/'+event.eventid

        data=copy.deepcopy(data)
        self.data=data
       
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


    def toGeoJSON(self,filename=None):

        text=json.dumps(self.data)
        if filename:
            with open(filename,'w') as f:
                f.write(text)
        return text


    # Called by Product with format 'png'
    def toImage(self):
      
        dataName=self.data['name']

        inputfile='%s/dyfi_%s.geojson' % (self.dir,dataName)
        outputfile='%s/dyfi_%s.png' % (self.dir,dataName)

        return Map.GeoJSONtoImage(inputfile,outputfile,self.config)


    def GeoJSONtoImage(inputfile,outputfile,config):

        """
        :synopsis: Create static image map from Event object
        :returns: none
        """

        leafletdir=config.directories['leaflet'] 
        leafletdatafile='%s/data.js' % leafletdir
        pngfile='%s/screenshot.png' % leafletdir
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

        out=open(leafletdir+'/tmp.stdout.txt','wb')
        err=open(leafletdir+'/tmp.stderr.txt','wb')
        print('Map.GeoJSONtoImage: Running subprocess with command:')
        print(' '.join(command))
        try:
            subprocess.call(command,cwd=leafletdir,stdout=out,stderr=err,timeout=30)
        except:
            raise NameError('Something wrong with subprocess call!') 

        print('Map.GeoJSONtoImage: ...Done.')

        shutil.copyfile(pngfile,outputfile)
        out.close
        err.close
        return outputfile


