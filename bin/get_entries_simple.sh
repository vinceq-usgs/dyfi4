#! /bin/bash

#############################################
#
# Update this for your configuration
#
#############################################

MYHOST='dyfit'
declare -a SERVERS
SERVERS=(vinceq@igskahcgvmp1ct1.cr.usgs.gov vinceq@igskmncgvmp2ct1.cr.usgs.gov)
INPUTDIR='/var/www/data/earthquake-dyfi-response/incoming.vm'$MYHOST
TIMEOUT=15
DESTINATION=./data/incoming

#############################################
#
# End configuration section
#
#############################################

for SERVER in "${SERVERS[@]}"
do
    getcommand="/usr/bin/rsync --verbose --exclude 'tmp.*' --timeout=$TIMEOUT -ulpotgrz $SERVER:$INPUTDIR/. $DESTINATION"
    echo $getcommand
    echo $($getcommand)
done

echo 'Entries in '$DESTINATION':'
echo $(ls -1 $DESTINATION | wc | awk '{print $1}')
