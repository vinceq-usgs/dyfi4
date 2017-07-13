"""
Config
======
    
"""

import yaml
from types import SimpleNamespace

class Config:

    """

    :synopsis: Handle DYFI configuration options.
    :param str configfile: YAML file with configuration options
    
    .. attribute:: hash
        
        Dict of configuration sections suitable for __iter__.
        

    Usage:
    
    from dyfi import Config
    config=Config(someyamlfile)
    config=Config() # defaults to ./config.yml
    
    recipient=config.mail['to']
    
"""

    def __init__(self,file='./config.yml'):

        with open(file,'r') as f:
            configs=yaml.load(f)

        self.hash={}

        for key in configs:
            val=configs[key]

            self.hash[key]=val
            setattr(self,key,val)

    def __iter__(self):
        return iter(self.hash.keys())
    
    def __repr__(self):
        output=''
        for section,val in self.hash.items():
            output=output+'section'+':\n'
            output=output+(str(val))

        return output
