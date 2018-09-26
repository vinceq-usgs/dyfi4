import shutil
import tempfile
import os
import subprocess
import json
import copy
import datetime

class Map:
    """
    :synopsis: Collects data to create a static map
    :param str name: Name for the map
    :param event: A :py:class:`dyfi.Event` object
    :param data: Aggregated data in `GeoJSON` format
    :param config: A :py:class:`dyfiConfig` object
    :param str eventDir: (optional) event directory (default `data/[eventid]/`)

    This handles the rendering of DYFI data (aggregated entries in GeoJSON format) into plottable data for `Leaflet`.

    """

    def __init__(self,name,event,data,config,eventDir=None):

        print('Map: Creating',name,'object.')
        self.name=name
        self.event=event
        self.config=config
        self.dir=eventDir

        if not eventDir:
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
                'magnitude':event.mag,
                'depth':event.depth,
                'id':event.eventid,
            }
        }
        data['features'].append(epicenter)

        # Add map display data to data.properties
        p=data['properties']
        p['id']=event.eventid
        p['date']=event.eventdatetime+' (UTC)'
        p['mag']=event.mag
        p['lat']=event.lat
        p['lon']=event.lon
        p['depth']=event.depth
        p['process_time']=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        p['version']=event.ciim_version or 1

        self.data=data


    def toGeoJSON(self,filename=None):
        """

        :synopsis: Convert this map object into GeoJSON
        :param str filename: (optional) filename
        :returns: prettyprinted GeoJSON text


        This prints out the GeoJSON data used for the static images, not the actual GeoJSON data. Hence it's only used for debugging.

        If `filename` is specified, the data is saved to that file.

        """

        text=json.dumps(self.data,sort_keys=True,indent=2)
        if filename:
            with open(filename,'w') as f:
                f.write(text)
        return text


    def toImage(self):
        """

        :synopsis: Creates the PNG static image
        :returns: The resulting filename

        Calls :py:func:`GeoJSONtoImage` with the appropriate parameters. Normally, this is called during the processing of a :py:class:`dyfi.products.Product` object.

        """
        dataName=self.name

        outputfile='%s/dyfi_%s.png' % (self.dir,dataName)
        print('Map.toImage() with filename',outputfile)
        return Map.GeoJSONtoImage(self.data,outputfile,self.config)


    @staticmethod
    def GeoJSONtoImage(inputdata,outputfile,config):

        """
        :synopsis: Create a static image from a GeoJSON file
        :param inputdata: The input GeoJSON file (str) or GeoJSON object
        :param str outputfile: The resulting PNG file
        :returns: The resulting output file

        Creates the static image using Leaflet to render the map and a screenshot application. See the :ref:`Creating static products` for details.

        """

        leafletdir=config.directories['leaflet']

        # This creates a temporary JS file in ./leaflet which is just
        # a GeoJSON file but with VAR= to make it valid JavaScript.
        # This is a lot easier than dealing with browser CORS shenanigans.

        if isinstance(inputdata,str):
            with open(inputdata,'r') as jsonText:
                outputtext=jsonText.read()
        else:
            outputtext=json.dumps(inputdata,sort_keys=True,indent=2)

        tmpfilename=None
        with tempfile.NamedTemporaryFile(mode='w',prefix='tmp.Map.', suffix='.js',dir=leafletdir,delete=False) as tmp:
            tmpfilename=tmp.name
            tmp.write('data='+outputtext+';\n')

        if (not tmpfilename
            or not os.path.isfile(tmpfilename)
            or os.path.getsize(tmpfilename)<10):
            print('WARNING: bad or missing temporary JSON file, removing.')
            os.remove(tmpfilename)
            return

        # Make a copy in leaflet directory for debugging purposes
        shutil.copy(tmpfilename,leafletdir+'/data.js')

        # Now run screenshot program
        command=config.executables['screenshot']
        command=[line.replace('__ABSPATH__',os.path.abspath(leafletdir))
            for line in command]
        command.append(tmpfilename)
        command.append(tmpfilename+'.png')
        if '_thumbnail' in outputfile:
            command.append('-thumbnail')

        with open(leafletdir+'/log.stdout.txt','wb') as logOut,open(leafletdir+'/log.stderr.txt','wb') as logErr:

            print('Map.GeoJSONtoImage: Running subprocess with command:')
            print(' '.join(command))

            try:
                subprocess.call(command,cwd=leafletdir,stdout=logOut,stderr=logErr,timeout=60)
            except:
                raise RuntimeError('Something wrong with subprocess call!')

            shutil.move(tmpfilename+'.png',outputfile)
            print('Map.GeoJSONtoImage: ...Done, created',outputfile)
            os.remove(tmpfilename)

        return outputfile


