from distutils.core import setup

# Copied from usgs/pager repo, not yet tested

setup(name='dyfi',
      version='0.0.5',
      description='Did You Feel It? (DYFI)',
      author='Vince Quitoriano',
      author_email='vinceq@contractor.usgs.gov',
      url='',
      packages=['dyfi','util/modules'],
      scripts=['app/rundyfi.py','app/makescreenshot.py','app/makemovie.py','util/queueTriggers.py','util/loadEntries.py','util/updateEvent.py']
)
