import boto3

from env.envMgr import getEnv, setAwsRegion
from env.envKeyDef import AwsIam, Dynamodb

# AWS接続設定
awsAccessKeyId     = getEnv(AwsIam.ACCESS_KEY_ID)
awsSecretAccessKey = getEnv(AwsIam.SECRET_ACCESS_KEY)
# DynamoDB接続設定
tableName    = getEnv(Dynamodb.TABLE)
partitionKey = getEnv(Dynamodb.PARTI)
partition    = {partitionKey: '0'}

setAwsRegion()

dynamodb = boto3.resource('dynamodb',
    aws_access_key_id     = awsAccessKeyId,
    aws_secret_access_key = awsSecretAccessKey)

def getLastNewsTitle():
    table = dynamodb.Table(tableName)
    lastNewsInfo = table.get_item(Key=partition)
    return lastNewsInfo['Item']['title']

def updateLastNewsTitle(title):
    table = dynamodb.Table(tableName)
    return table.update_item(
        Key=partition,
        UpdateExpression="set title = :title",
        ExpressionAttributeValues={
            ':title': title
        }
    )