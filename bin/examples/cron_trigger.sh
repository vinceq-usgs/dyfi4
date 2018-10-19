#! /bin/bash
# Example script to process events with pending entries.
# Run this every minute from cron, or less often depending on system resources.

# CONFIGURATION VARIABLES
DYFI=/path/to/dyfi4
PATH=$PATH:/path/to/conda/bin

. activate dyfi

cd $DYFI
$DYFI/util/queueTriggers.py --maxruns 5 >$DYFI/log/queue.log 2>$DYFI/log/queue.err

