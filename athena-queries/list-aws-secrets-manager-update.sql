SELECT eventname
FROM cloudtrail_logs_new 
WHERE 
    awsregion = 'us-west-2' 
    AND recipientaccountid = '586672212047' 
    AND account = '586672212047'
    AND region = 'us-west-2'
    AND year = '2024'
    AND month = '06'
    AND day = '04';
