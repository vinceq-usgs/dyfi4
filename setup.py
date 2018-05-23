from distutils.core import setup

# Copied from usgs/pager repo, not yet tested

setup(name='dyfi',
      version='0.0.4',
      description='Did You Feel It? (DYFI)',
      author='Vince Quitoriano',
      author_email='vinceq@usgs.gov',
      url='',
      packages=['dyfi'],
      scripts=['app/rundyfi.py','app/makescreenshot.py','app/makemovie.py']
)
