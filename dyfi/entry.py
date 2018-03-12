class Entry():
    """

    :synopsis: Class for handling user questionnaire responses
    :param dict rawdata: raw data from one row of an extended table

    This holds data for a particular user entry (as loaded from the `extended` database).

    .. warning::
        An Entry object contains raw data and may have PII
        or invalid location data. DO NOT EXPORT `Entry` OBJECTS!

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
        'felt','other_felt',
        'motion','reaction','stand','shelf','picture',
        'furniture','damage','d_text'
    ]


    def __init__(self,rawdata):

        self.table='extended'

        # Initialize attributes

        for column in Entry.columns:
            val=rawdata[column] if column in rawdata else None
            setattr(self,column,val)


    def index(self,index):
        """
            :synopsis: Return the numeric, cleaned-up version of a questionnaire index for CDI computation
            :param str index: name of an column

        """

        if index in Entry.cdicolumns:
            val=getattr(self,index)

        else:
            raise AttributeError('Invalid Entry index '+index)

        # Special case for 'd_text' requires string

        if index=='d_text':
            return self.d_text

        # For everything else, we need a numeric value. If the raw value is a string with comments, extract the numeric value.

        if isinstance(val,str):
            val=val.split(' ')[0]

            if '.' in val:
                val=float(val)
            else:
                val=int(val)

        return val


    def __str__(self):
        text='[Entry: subid:%s, intensity:%s]' % (
            self.subid,self.user_cdi)
        return text


    def __repr__(self):
        text=''
        for column in Entry.columns:
            val=str(getattr(self,column))
            text=text+column+':'+val+','

        text='Entry('+text[:-1]+')'
        return text

