send_slack_message () {
    curl -s --header "Authorization: Bearer $SLACK_AUTH_TOKEN" \
        --form  channel=$CHANNEL --form text="$1" \
         https://slack.com/api/chat.postMessage > slack.log
}

case $1 in
    Production)
        DIR='/media/toll'
        CHANNEL='inf-information_systems_no-interns';;
    *)
        DIR='/media/test'
        CHANNEL='srs-testing';;
esac

send_slack_message "Unzip Toll File $1" 

tar -xzf /media/pload/toll.tar.gz -C "$DIR"
rm /media/pload/toll.tar.gz

if tar -xzf /media/pload/toll.tar.gz -C "$DIR"; then
    rm /media/pload/toll.tar.gz
else
    send_slack_message "Error extracting toll file $1" 
    exit 1
fi

send_slack_message "Unzip complete, delete folders older than 13 months."

for FILE in `ls $DIR -r | sed -n '14,19p'`
do
  rm -r $DIR/$FILE
done

send_slack_message "Toll Statements Complete"

python3 manage.py send_email --email TOLL_COMPLETE