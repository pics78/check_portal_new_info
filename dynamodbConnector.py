import os
import boto3

table_name = os.environ['DYNAMODB_TABLE_NAME']
partition_key = os.environ['DYNAMODB_PARTITION_KEY']
partition = {partition_key: '0'}

os.environ['AWS_DEFAULT_REGION'] = 'ap-northeast-1'

dynamodb = boto3.resource('dynamodb',
    aws_access_key_id=os.environ['ACCESS_KEY_ID'],
    aws_secret_access_key= os.environ['SECRET_ACCESS_KEY'])

def getLastNewsTitle():
    table = dynamodb.Table(table_name)
    lastNewsInfo = table.get_item(Key=partition)
    return lastNewsInfo['Item']['title']

def updateLastNewsTitle(title):
    table = dynamodb.Table(table_name)
    return table.update_item(
        Key=partition,
        UpdateExpression="set title = :title",
        ExpressionAttributeValues={
            ':title': title
        }
    )