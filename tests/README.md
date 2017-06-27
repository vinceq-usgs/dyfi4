DYFI4 TEST SUITE
----------------

DATABASE
=======

This repository includes a copy of the DYFI4 database in separate
SQLite tables:

1. Event table. This holds event information for all events that have triggered DYFI.
  
2. Maps table. A separate table that holds map-specific information, such as custom zoom levels and map offsets. This table is being phased out.

3. Extended tables. These are records of raw individual entries, one for each year. Only a partial dataset is provided: all DYFI events, and 2015 and 2016 entries. Personal information has been redacted (the name, email, phone, and comments fields).

INSTALLATION
============

Before running tests, edit config.yml to fill in the correct email addresses, SMTP server, and correct test database (if you have your own).

TESTING
=======
To run all tests:
pytest ./test.py
