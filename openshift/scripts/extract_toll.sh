send_slack_message () {
    curl -s --header "Authorization: Bearer $SLACK_AUTH_TOKEN" \
        --form  channel=srs-errors --form text="$1" \
         https://slack.com/api/chat.postMessage > slack.log
}

send_slack_message "Unzip Toll File"

unzip -q /media/pload/toll.zip -d /media/toll
rm /media/pload/toll.zip

send_slack_message "Unzip complete, delete folders older than 13"

for FILE in `ls -r | sed -n '14,19p'`
do
  rm -r $FILE
done

send_slack_message "Toll Statements Complete"