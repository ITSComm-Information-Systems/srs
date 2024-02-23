send_slack_message () {
    curl -s --header "Authorization: Bearer $SLACK_AUTH_TOKEN" \
        --form  channel=srs-testing --form text="$1" \
         https://slack.com/api/chat.postMessage > slack.log
}

send_slack_message "Unzip Toll File $1" 

echo $1

if [ $1 == 'Production' ]
then
    DIR='/media/toll'
else
    DIR='/media/test'
fi

unzip -q /media/pload/toll.zip -d $DIR
rm /media/pload/toll.zip

send_slack_message "Unzip complete, delete folders older than 13"

for FILE in `ls $DIR -r | sed -n '14,19p'`
do
  rm -r $DIR/$FILE
done

send_slack_message "Toll Statements Complete"