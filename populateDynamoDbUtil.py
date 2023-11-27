import boto3
import os
import json
from dotenv import load_dotenv
load_dotenv()

DYNAMODB_SERVICE = os.getenv("DYNAMODB_SERVICE")
TABLE_NAME = os.getenv("TABLE_NAME")
AWS_REGION = os.getenv("REGION")
AWS_ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")

dynamodbClient = boto3.resource(
    DYNAMODB_SERVICE,
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
table = dynamodbClient.Table(TABLE_NAME)
with open('/Users/diyabiju/Documents/GitHub/CSE546-FaceRecognition/student_data.json', 'r') as json_file:
    items = json.load(json_file)
for item in items:
    table.put_item(
        Item={
            'id': item['id'],
            'major': item['major'],
            'name': item['name'],
            'year': item['year']
        }
    )