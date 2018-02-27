class Entry():
    """

    :synopsis: Class for handling user questionnaire responses
    :param dict rawdata: raw data from one row of an extended table

    This holds data for a particular user entry (as loaded from the `extended` database).

    .. warning::
        An Entry object contains raw data and may have PII
        or invalid location data. DO NOT EXPORT `Entry` OBJECTS!

    .. note::
        Access the data in this object with the keys in
        `Entry.columns` as attributes,  e.g. `entries.eventid`
        or `event.felt`.

    .. data:: columns

        A list of all the columns in the extended tables.

    .. data:: cdicolumns

        A subset of extended columns used for intensity calculation.

    """

    columns=[
        'subid','eventid','orig_id','suspect',
        'region','usertime','time_now',
        'latitude','longitude','geo_source','zip','zip_4',
        'city','admin_region','country',
        'street','name','email','phone',
        'situation','building','asleep',
        'felt','other_felt','motion','duration','reaction',
        'response','stand','sway','creak','shelf',
        'picture','furniture','heavy_appliance','walls','slide_1_foot',
        'd_text','damage','building_details','comments','user_cdi',
        'city_latitude','city_longitude','city_population',
        'zip_latitude','zip_longitude','location','tzoffset',
        'confidence','version','citydb','cityid'
    ]

    cdicolumns=[
        'subid','table','latitude','longitude','felt','other_felt',
        'motion','reaction','stand','shelf','picture',
        'furniture','damage'
    ]

    def __init__(self,rawdata):
        self.table='extended'

        for column in Entry.columns:
            if column in rawdata.keys():
                self.__dict__[column]=rawdata[column]
            else:
                self.__dict__[column]=None


    def __str__(self):
        text='[Entry: subid:%s, intensity:%s]' % (
            self.subid,self.user_cdi)
        return text


    def __repr__(self):
        text=''
        for column in Entry.columns:
            if self.__dict__[column]:
                val=str(self.__dict__[column])
                text=text+column+':'+val+','

        text='Entry('+text[:-1]+')'
        return text

