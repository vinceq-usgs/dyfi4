#! /bin/bash

#############################################
#
# Update this for your configuration
#
#############################################

MYHOST='examplehost'
declare -a SERVERS
SERVERS=(host1.com host2.com)
INPUTDIR='/var/inputdirectory/incoming.'$MYHOST
TIMEOUT=10
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
    echo `$getcommand`
done

echo 'Entries in '$DESTINATION':'
echo `ls -1 $DESTINATION | wc | awk '{print $1}'`
