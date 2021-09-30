import boto3

from env.envMgr import getEnv, setAwsRegion
from env.envKeyDef import AwsIam, AwsAcc, Lambda

awsAccessKeyId     = getEnv(AwsIam.ACCESS_KEY_ID)
awsSecretAccessKey = getEnv(AwsIam.SECRET_ACCESS_KEY)

tableName = getEnv(AwsAcc.DDB_TABLE_NAME)
partition = { getEnv(AwsAcc.DDB_PARTI_KEY): '0' }

bucketName = getEnv(AwsAcc.S3_BUCKET_NAME)
expiresIn = getEnv(AwsAcc.S3_EXPIRESIN)

tmpDir = getEnv(Lambda.TMP_DIR)

setAwsRegion()

def AWSResource(service):
    return boto3.resource(service,
        aws_access_key_id     = awsAccessKeyId,
        aws_secret_access_key = awsSecretAccessKey)

def AWSClient(service):
    return boto3.client(service,
        aws_access_key_id     = awsAccessKeyId,
        aws_secret_access_key = awsSecretAccessKey)

ddbResrc = AWSResource('dynamodb')
s3Resrc  = AWSResource('s3')
s3client = AWSClient('s3')

def getLastNewsTitle():
    table = ddbResrc.Table(tableName)
    lastNewsInfo = table.get_item(Key=partition)
    return lastNewsInfo['Item']['title']

def updateLastNewsTitle(title):
    table = ddbResrc.Table(tableName)
    return table.update_item(
        Key=partition,
        UpdateExpression="set title = :title",
        ExpressionAttributeValues={
            ':title': title
        }
    )

def uploadFileToS3(fileName):
    s3Resrc.Bucket(bucketName).upload_file(tmpDir + fileName, fileName)

def getFileUrl(fileName):
    return s3client.generate_presigned_url(
        ClientMethod = 'get_object',
        Params       = {'Bucket': bucketName, 'Key': fileName},
        ExpiresIn    = expiresIn,
        HttpMethod   = 'GET'
    )