#! /usr/bin/env python3

"""
dyfi
====

Command line tool to create products for a given event.
This will also run the 'push' tool to send products to PDL
if the '-push' flag is used.

# NOTE: Do not geocode here. Geocoding should be done from
# command line or 'event' daemon.

"""
import time
import argparse

from context import dyfi
from dyfi import Config,Db,Event,Maps,Entries,Products

def main(args=None):

    print('--------------------')
    print('Starting dyfi.py: ',time.asctime(time.localtime()))

    # Handle arguments
    
    parser=argparse.ArgumentParser(
        description='Create DYFI products for a given event'
    )
    parser.add_argument(
        'evid',type=str,
        help='Event ID'
    )
    parser.add_argument(
        '--push',action='store_true',
        help='Push event products to PDL'
    )
    parser.add_argument(
        '--configfile',action='store',default='./config.yml',
        help='Specify config file'
    )
  
    if not args: 
      args=parser.parse_args()
    print(repr(args))

    evid=args.evid

    # Load config file
    config=Config(args.configfile)
    
    # Open database connection
    db=Db(config)
    
    # Load data from database
    event=Event(db.loadEvent(evid))

    if not event:
        raise NameError('No data for event '+evid)

    # Load map params
    maps=Maps(db.loadMaps(evid))
    if not maps.maplist:
        print('WARNING: No maps found for this event, using defaults')
        
    # Load entries
    rawentries=Entries(db.loadEntries(event=event))
        
    # Create products
    # contents.xml should be created in createProducts

    products=Products(
        event=event,
        maps=maps,
        rawentries=rawentries
    )
    productlist=products.create()
    print(productlist)
    
    print('Done with',evid)
            

if __name__=='__main__':
    main()
