from distutils.core import setup

# Copied from usgs/pager repo, not yet tested

setup(name='dyfi',
      version='0.0.2',
      description='Did You Feel It? (DYFI)',
      author='Vince Quitoriano',
      author_email='vinceq@usgs.gov',
      url='',
      packages=['dyfi'],
      scripts=['bin/rundyfi.py']
)
