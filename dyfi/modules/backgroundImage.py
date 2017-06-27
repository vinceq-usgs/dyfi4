"""

backgroundImage
===============

Replicating the functionality of Basemap.argisonline() because
it doesn't seem to be working properly.

"""


import tempfile
import requests
from PIL import Image

#TODO: Put this in a config file
service='World_Street_Map'
#service='World_Terrain_Base'
#service='World_Imagery'
#service='World_Topo_Map'

server='http://services.arcgisonline.com' \
    +'/arcgis/rest/services/'+service+'/MapServer/export'


def addImage(self):

    # TODO: Instead of a temporary file, save image file
    # and check for previous image files before downloading
    
    imagefile=tempfile.NamedTemporaryFile(
        dir='.',
        prefix='tmp.backgroundImage.',
        suffix='.png',
        delete=True)

    m=self.m

    bbox='%s,%s,%s,%s' % (self.west,
                          self.south,self.east,self.north)
    params={
        'bbox':bbox,
        'bboxSR':4326,
        'format':'png',
        'transparent':False,
        'f':'image',
        'size':'600,600',
    }

    print('Requesting image:')
    r = requests.get(server,params=params)
    if r.status_code==200:
        print('Writing to',imagefile.name)
        for chunk in r:
            imagefile.write(chunk)

    else:
        print('Plot: addBaseImage failed, skipping.')
        return

    print('Finished downloading image.')

    image=Image.open(imagefile)
    image.transpose(Image.FLIP_TOP_BOTTOM)
    m.imshow(image.transpose(Image.FLIP_TOP_BOTTOM),
             aspect='auto',zorder=2)

    return

