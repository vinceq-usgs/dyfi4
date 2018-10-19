#! /usr/bin/env python
"""

Usage: bin/makeAuxdata.py evid

Create files used by the Event Pages to populate the DYFI Product page:
  event_data.xml
  [event]_ciim_geo.jpg
  [event]_cdi_zip.xml
   

"""

import sys
import argparse
import shutil
import os.path
import yaml
import json
import defusedxml.minidom as minidom
import subprocess

parser=argparse.ArgumentParser(
    prog='bin/makeAuxdata.py',
    description='Create additional datafiles for Event Pages'
)
parser.add_argument(
    'evid',action='store',
    help='Event ID'
)
parser.add_argument(
    '--configfile',action='store',default='./config.yml',
    help='Specify config file'
)

parser.add_argument(
    '--localconfigfile',action='store',default='bin/localconfig.yml',
    help='Specify local config file'
)


def getParams(event,config,dataDir):

    params={
        'evid':event.eventid,
        'event':event,
        'template':None
    }
    
    with open(config['event_dataTemplate'],'r') as f:
        template=yaml.safe_load(f)
        params['template']=template
        paramList=template['paramList']
        paramListConversion=template['paramListConversion']

    for p in paramList:
        if p in paramListConversion:
            val=getattr(event,paramListConversion[p])
        else:
            val=getattr(event,p)
        params[p]=str(val)

    params['network']=event.source
    params['eventid']=event.eventid[2:]
    params['dir']=dataDir

    for p in ('event_version','nresponses','max_intensity'):
        if params[p]=='None': params[p]='0'

    if params['code_version']=='None': params['code_version']='V4'
    
    return params


def createEventDataXml(params):

    template=params['template']
    event_dataAttrs=template['event_dataAttrs']
    eventAttrs=template['eventAttrs']
    cdi_summaryAttrs=template['cdi_summaryAttrs']
    categories=template['productCategories']

    outputfile=params['dir']+'/event_data.xml'
    xml=minidom.parseString('<?xml version="1.0" encoding="UTF-8"?><event_data />')

    event_dataNode=xml.childNodes[0]
    for p in event_dataAttrs:
        event_dataNode.setAttribute(p,params[p])

    eventNode=event_dataNode.appendChild(xml.createElement('event'))
    for p in eventAttrs:
        eventNode.setAttribute(p,params[p])

    cdi_summaryNode=event_dataNode.appendChild(xml.createElement('cdi_summary'))
    for p in cdi_summaryAttrs:
        cdi_summaryNode.setAttribute(p,params[p])

    productsNode=event_dataNode.appendChild(xml.createElement('products'))
    for category in categories:
        categoryNode=productsNode.appendChild(xml.createElement('category'))
        categoryNode.setAttribute('name',category)
        for product in xmlProducts(xml,category,template):
            categoryNode.appendChild(product)

    data=xml.toprettyxml(indent='  ',newl='\n')
    with open(outputfile,'w') as f:
        f.write(data)

    print('Created',outputfile)
    return outputfile


def xmlProducts(xml,category,template):

    productsList=template['productCategories'][category]
    products=[]

    for p in productsList:
        node=xml.createElement('product')
        node.setAttribute('name',p['name'])
        descNode=node.appendChild(xml.createElement('description'))
        descNode.appendChild(xml.createTextNode(p['description']))
        formatNode=node.appendChild(xml.createElement('format'))
        formatNode.setAttribute('file',p['file'])
        formatNode.setAttribute('type',_getType(p['file'],template))

        products.append(node)

    return products


def _getType(filename,template):

    formats=template['formatTypes']
    ext=filename.split('.')[1]

    return formats[ext]



def createCdiZipXml(params):
    # This creates a fake cdi_zip.xml for the current Event Pages
    # 'DYFI Responses' tab using the geocoded data.

    outputfile=params['dir']+'/cdi_zip.xml'
    xml=minidom.parseString('<?xml version="1.0" encoding="UTF-8"?><cdidata/>')

    with open(params['dir']+'/dyfi_geo_10km.geojson','r') as f:
        jsondata=json.load(f)

    cdidataNode=xml.childNodes[0]
    cityNode=cdidataNode.appendChild(xml.createElement('city'))

    for location in jsondata['features']:
        p=location['properties']
        locdata={
            'cdi':p['cdi'],
            'nresp':p['nresp'],
            'dist':p['dist'],
            'lat':p['center']['coordinates'][1],
            'lon':p['center']['coordinates'][0],
            'name':p['name']
        }

        formattedName=p['name']+'::10km grid'+'::Aggregated'
        locNode=cityNode.appendChild(xml.createElement('location'))
        locNode.setAttribute('name',formattedName)
        for k,v in locdata.items():
            pNode=locNode.appendChild(xml.createElement(k))
            pNode.appendChild(xml.createTextNode(str(v)))
   
    data=xml.toprettyxml(indent='  ',newl='\n')
    with open(outputfile,'w') as f:
        f.write(data)

    print('Created',outputfile)
    return outputfile

    

def main(args):

    sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from dyfi import Config,Event

    evid=args.evid
    config=Config(args.configfile)
    localconf=Config(args.localconfigfile)
    dataDir='%s/%s' % (localconf.directories['data'],evid)

    event=Event(evid,config=config)

    # Create [eventid]_ciim_geo.jpg to display
    # This is just a copy of the dyfi_geo_10km.png file

    originalFile='%s/dyfi_map_geo_10km.png' % dataDir
    destFile='%s/%s_ciim_geo.jpg' % (dataDir,evid)
    shutil.copy(originalFile,destFile)
    print('Created',destFile)

    params=getParams(event,localconf.aux,dataDir)
    createEventDataXml(params)
    createCdiZipXml(params)


if __name__=='__main__':
    args=parser.parse_args()
    main(args)

