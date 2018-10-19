#! /bin/bash
# Example script to get entries from a remote server(s), then process them.
# Run this every minute from cron, or less often depending on system resources.

# CONFIGURATION VARIABLES
DYFI=/path/to/dyfi4
PATH=$PATH:/path/to/conda/bin

. activate dyfi

cd $DYFI
$DYFI/bin/get_entries_simple.sh >$DYFI/log/entries.log 2>$DYFI/log/entries.err
$DYFI/util/loadEntries.py >>$DYFI/log/entries.log 2>>$DYFI/log/entries.err

