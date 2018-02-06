import yaml

class Config:
    """

    :synopsis: Handle DYFI configuration options
    :param str configfile: YAML file with configuration options (default `./cofig.yml`)

    .. attribute:: sections

        Dict of configuration sections suitable for __iter__.

    A general class to handle configuration options using a `YAML` config file.
    See the :ref:`Implementation Guide` for details.

    Usage::

      from dyfi import Config
      config=Config()
      config=Config('./custom.yml')

    To access values::

      dbconfigs=config.db # A hash of database configs
      dbfiles=config.db['files']
      eventdbfile=config.db['files']['event']

    Looping through config sections::

      for section in config:
        print(section) # prints a list of sections

    Prettyprint all configs::

      print(config) # prettyprints all configs

"""

    def __init__(self,file='./config.yml'):

        with open(file,'r') as f:
            configs=yaml.safe_load(f)

        self.sections={}

        for key in configs:
            val=configs[key]

            self.sections[key]=val
            setattr(self,key,val)


    def __iter__(self):
        return iter(self.sections.keys())


    def __repr__(self):
        output=''
        for key,val in self.sections.items():
            output=output+key+':'+str(val)+'\n'

        return output

