#! /bin/bash

declare -a SERVERS

# CONFIGURATION VARIABLES
# Update these for your remote server architecture
MYHOST='thishost'
SERVERS=(user@server1.com user@server2.com)
INPUTDIR='/remotedirectory/incoming.'$MYHOST
DESTINATION='./data/incoming'
RSYNC_COMMAND='/usr/bin/rsync'
RSYNC_OPTIONS='--verbose --exclude "tmp.*" --timeout=15 -ulpotgrz --remove-sent-files'


for SERVER in "${SERVERS[@]}"
do
    getcommand="$RSYNC_COMMAND $RSYNC_OPTIONS $SERVER:$INPUTDIR/. $DESTINATION"
    echo $getcommand
    echo $($getcommand)
done

echo 'Files in '$DESTINATION':'
echo $(ls -1 $DESTINATION | wc | awk '{print $1}')

