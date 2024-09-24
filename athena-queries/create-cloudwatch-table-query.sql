/*
 There's some freaking BS hidden link that  You have to click on CloudTrail on the actual trail link to actually see the CloudTrail. If you actually go to the bucket you won't see the folders. It's really stupid.
*/
CREATE EXTERNAL TABLE IF NOT EXISTS cloudtrail_logs_new (
  eventversion string COMMENT 'from deserializer', 
  useridentity struct<type:string,principalid:string,arn:string,accountid:string,invokedby:string,accesskeyid:string,username:string,sessioncontext:struct<attributes:struct<mfaauthenticated:string,creationdate:string>,sessionissuer:struct<type:string,principalid:string,arn:string,accountid:string,username:string>>> COMMENT 'from deserializer', 
  eventtime string COMMENT 'from deserializer', 
  eventsource string COMMENT 'from deserializer', 
  eventname string COMMENT 'from deserializer', 
  awsregion string COMMENT 'from deserializer', 
  sourceipaddress string COMMENT 'from deserializer', 
  useragent string COMMENT 'from deserializer', 
  errorcode string COMMENT 'from deserializer', 
  errormessage string COMMENT 'from deserializer', 
  requestparameters string COMMENT 'from deserializer', 
  responseelements string COMMENT 'from deserializer', 
  additionaleventdata string COMMENT 'from deserializer', 
  requestid string COMMENT 'from deserializer', 
  eventid string COMMENT 'from deserializer', 
  resources array<struct<arn:string,accountid:string,type:string>> COMMENT 'from deserializer', 
  eventtype string COMMENT 'from deserializer', 
  apiversion string COMMENT 'from deserializer', 
  readonly string COMMENT 'from deserializer', 
  recipientaccountid string COMMENT 'from deserializer', 
  serviceeventdetails string COMMENT 'from deserializer', 
  sharedeventid string COMMENT 'from deserializer', 
  vpcendpointid string COMMENT 'from deserializer'
)
PARTITIONED BY ( 
  account string, 
  region string, 
  year string,
  month string,
  day string
)
ROW FORMAT SERDE 
  'com.amazon.emr.hive.serde.CloudTrailSerde' 
STORED AS INPUTFORMAT 
  'com.amazon.emr.cloudtrail.CloudTrailInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://aws-controltower-logs-309059759820-us-east-2/o-j5vlb2756v/AWSLogs/o-j5vlb2756v'
TBLPROPERTIES (
  'projection.enabled'='true', 
  'projection.account.type'='enum', 
  'projection.account.values'='279268920118,931158682400,375777745621,442893166637,309059759820,983594525606,790685595415,251530377535,961556819121,923261199481,690994262422,590472111969,526083761887,285225641387,208648672950,586672212047,862317026126,473742870145,463931586000,144487101178,703548811235', 
  'projection.region.type'='enum', 
  'projection.region.values'='us-east-2,us-east-1,us-west-1,us-west-2,af-south-1,ap-east-1,ap-south-1,ap-northeast-3,ap-northeast-2,ap-southeast-1,ap-southeast-2,ap-northeast-1,ca-central-1,eu-central-1,eu-west-1,eu-west-2,eu-south-1,eu-west-3,eu-north-1,me-south-1,sa-east-1', 
  'projection.year.type'='integer', 
  'projection.year.range'='2019,2025', 
  'projection.month.type'='integer', 
  'projection.month.range'='1,12', 
  'projection.day.type'='integer', 
  'projection.day.range'='1,31', 
  'storage.location.template'='s3://aws-controltower-logs-309059759820-us-east-2/o-j5vlb2756v/AWSLogs/o-j5vlb2756v/${account}/CloudTrail/${region}/${year}/${month}/${day}'
);
