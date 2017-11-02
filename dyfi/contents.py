from collections import OrderedDict
import os.path
import defusedxml.minidom as minidom

class Contents:

    """

productContents
===============

:synopsis: Create a :ref:`contents.xml` file used by the Earthquake Pages.

.. data:: PRODUCT_TYPES

An OrderedDict of the product types and the titles used for Event Pages formatting.

.. data:: FORMAT_TYPES

An OrderedDict of the available formats and their corresponding MIME types.

    """

    PRODUCT_TYPES=OrderedDict((
      ("_ciim",{
            "title":"DYFI City Map",
            "id":"cityMap",
            "caption":"Map of responses by city or ZIP code"
        }),
      ("_ciim_geo",{
            "title":"DYFI Geocoded Map",
            "id":"geoMap",
            "caption":"Map of responses by geocoded location",
        }),
      ("_ciim_geocode",{
            "title":"DYFI Geocoded Map",
            "id":"geoMap",
            "caption":"Map of responses by geocoded location",
        }),
      ("_ciim_zoom",{
            "title":"DYFI Zoom Map",
            "id":"zoomMap",
            "caption":"Map of responses by city or ZIP code",
        }),
      ("_ciim_zoomin",{
            "title":"DYFI Zoom Map",
            "id":"zoomMap",
            "caption":"Map of responses by city or ZIP code",
        }),
      ("_ciim_zoomout",{
            "title":"DYFI Zoomout Map",
            "id":"zoomoutMap",
            "caption":"Map of responses by city or ZIP code",
        }),
      ("_plot_atten",{
            "title":"Intensity vs. Distance Plot",
            "id":"intDistPlot",
            "caption":"Plot of intensity vs. distance from hypocenter",
        }),
      ("_plot_numresp",{
            "title":"Responses vs. Time Plot",
            "id":"respTimePlot",
            "caption":"Plot of number or responses since event origin",
        }),
      ("cdi_zip",{
          "title":"Intensity Summary",
          "id":"intZipList",
          "caption":"Intensities aggregated by city or ZIP code",
        }),
      ("cdi_geo",{
          "title":"Intensity Summary (Geocoded)",
          "id":"intGeoList",
          "caption":"Intensities aggregated by UTM geocoded location",
        }),
      ("cdi_geo_1km",{
          "title":"Intensity Summary (Geocoded, 1km spacing)",
          "id":"intGeoList",
          "caption":"Intensities aggregated by UTM geocoded location",
        }),
      ("cdi_geo_10km",{
          "title":"Intensity Summary (Geocoded, 10km spacing)",
          "id":"intGeoList",
          "caption":"Intensities aggregated by UTM geocoded location",
        }),
      ("cdi_geocode",{
          "title":"Intensity Summary (Geocoded)",
          "id":"intGeoList",
          "caption":"Intensities aggregated by UTM geocoded location",
        }),
      ("dyfi",{
          "title":"DYFI Combined Geospatial Data",
          "id":"geospatial",
          "caption":"Combined maps for geospatial browsers",
        }),
      ("dyfi_zip",{
          "title":"DYFI Geospatial Data, ZIP and city aggregated",
          "id":"geospatial",
          "caption":"Combined maps for geospatial browsers",
        }),
      ("dyfi_geo_1km",{
          "title":"DYFI Geospatial Data, UTM aggregated (1km spacing)",
          "id":"geospatial",
          "caption":"Combined maps for geospatial browsers",
        }),
      ("dyfi_geo_10km",{
          "title":"DYFI Geospatial Data, UTM aggregated (10km spacing)",
          "id":"geospatial",
          "caption":"Combined maps for geospatial browsers",
        }),
      ("dyfi_plot_atten",{
          "title":"Plotting data for intensity-distance graph",
          "id":"intDistData",
          "caption":"Location intensities, mean, median and predicted values by hypocentral distance",
        }),
      ("dyfi_plot_numresp",{
          "title":"Plotting data for cumulative time graph",
          "id":"intTimeData",
          "caption":"Time past origin for cumulative number of entries",
        })
    ))

    FORMAT_TYPES = OrderedDict((
        ('txt','text/plain'),
        ('xml','text/xml'),
        ('jpg','image/jpeg'),
        ('png','image/png'),
        ('pdf','application/pdf'),
        ('ps','application/postscript'),
        ('json','application/json'),
        ('geojson','application/json'),
        ('_imap.html','text/html'),
        ('kmz','application/vnd.google-earth.kmz')
    ))

    def __init__(self,container):

        self.event=container.event
        self.dir=container.products.dir

        self.data=minidom.parseString('<?xml version="1.0"?><contents />')
        xml=self.data
        #root=xml.appendChild(xml.createElement('contents'))
        root=xml.childNodes[0]
        root.appendChild(xml.createComment('Full listing of files'))

        # Iterate through all product types and file types

        for ptype,pdata in self.PRODUCT_TYPES.items():
            basename=ptype
            if ptype[0]=='_':
                basename=self.event.eventid+ptype

            # Create XML node but don't attach it yet

            filenode=xml.createElement('file')
            filenode.setAttribute('title',pdata['title'])
            filenode.setAttribute('id',pdata['id'])
            caption=filenode.appendChild(
                xml.createElement('caption'))
            caption.appendChild(xml.createCDATASection(pdata['caption']))

            found=[]
            for filext in Contents.FORMAT_TYPES:
                if '.' in filext:
                    fullname=basename+filext
                else:
                    fullname=basename+'.'+filext

                pathname=self.dir+'/'+fullname
                if not os.path.isfile(pathname):
                    continue

                # Found this file
                found.append({'name':fullname,'type':filext})

            if not found:
                continue

            # Some files were found. Attach node now.

            root.appendChild(filenode)

            for filetype in found:
                fullname=filetype['name']
                filext=filetype['type']
                formatnode=filenode.appendChild(
                    xml.createElement('format'))
                formatnode.setAttribute('href',fullname)
                formatnode.setAttribute('type',Contents.FORMAT_TYPES[filext])

        # Now self.data is filled


    def toXML(self,save=None,filename=None):

        data=self.data.toprettyxml(indent='  ',newl='\n')
        if not save and not filename:
            return(data)

        if not filename:
            filename=self.dir+'/contents.xml'

        with open(filename,'w') as f:
            f.write(data)

        return filename

