
import yaml

class Config:

    """

    :synopsis: Handle DYFI configuration options
    :param str configfile: YAML file with configuration options

    .. attribute:: hash

        Dict of configuration sections suitable for __iter__.


    Usage::

      # To call:
      from dyfi import Config
      config=Config(someyamlfile)
      config=Config() # defaults to ./config.yml

      # Prettyprint all configs:
      print(config) # prettyprints all configs

      # Access a config value:
      recipient=config.mail['to']
      eventdbfile=config.db['files']['event']
      dbparams=config.directories # Get all directories

      # Loop through values
      for section in config: 
        print(section) # prints a list of sections

"""

    def __init__(self,file='./config.yml'):

        with open(file,'r') as f:
            configs=yaml.safe_load(f)

        self.hash={}

        for key in configs:
            val=configs[key]

            self.hash[key]=val
            setattr(self,key,val)


    def __iter__(self):
        return iter(self.hash.keys())


    def __repr__(self):
        output=''
        for key,val in self.hash.items():
            output=output+key+':'+str(val)+'\n'

        return output

