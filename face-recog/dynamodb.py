import boto3
import os

from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
load_dotenv()

DYNAMODB_SERVICE = os.getenv("DYNAMODB_SERVICE")
TABLE_NAME = os.getenv("TABLE_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")
AWS_REGION = os.getenv("REGION")
AWS_ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")

dynamodbClient = boto3.resource(
    DYNAMODB_SERVICE,
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def queryTable(resultName):
    table = dynamodbClient.Table(TABLE_NAME)
    response = table.query(
        IndexName=INDEX_NAME,
        KeyConditionExpression=Key('name').eq(resultName)
    )
    print(response['Items'])
    if response['Items'][0]: return response['Items'][0]
