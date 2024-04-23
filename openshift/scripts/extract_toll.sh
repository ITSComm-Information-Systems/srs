send_slack_message () {
    curl -s --header "Authorization: Bearer $SLACK_AUTH_TOKEN" \
        --form  channel=$CHANNEL --form text="$1" \
         https://slack.com/api/chat.postMessage > slack.log
}


case $1 in
    Production)
        DIR='/media/toll'
        CHANNEL='inf-information-systems_no-interns';;
    *)
        DIR='/media/test'
        CHANNEL='srs-testing';;
esac


if [ $1 == 'Production' ]
then
    DIR='/media/toll'
    CHANNEL='inf-information-systems_no-interns'
else
    DIR='/media/test'
    CHANNEL='srs-testing'
fi

send_slack_message "Unzip Toll File $1" 

unzip -q /media/pload/toll.zip -d $DIR
rm /media/pload/toll.zip

send_slack_message "Unzip complete, delete folders older than 13 months."

for FILE in `ls $DIR -r | sed -n '14,19p'`
do
  rm -r $DIR/$FILE
done

send_slack_message "Toll Statements Complete"

python3 manage.py send_email --mail TOLL_COMPLETE