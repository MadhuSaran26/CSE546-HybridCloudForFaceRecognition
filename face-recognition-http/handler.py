import os
import face_recognition
import pickle
import numpy as np
import json
import csv
from boto3.dynamodb.conditions import Key
import boto3
from dotenv import load_dotenv
load_dotenv()

INPUT_LOCAL_STORAGE_DIR = os.getenv("INPUT_LOCAL_STORAGE_DIR")
INPUT_FRAME_STORAGE_DIR = os.getenv("INPUT_FRAME_STORAGE_DIR")
ENCODING_PATH = os.getenv("ENCODING_PATH")
OUTPUT_FILE_DIRECTORY = os.getenv("OUTPUT_FILE_DIRECTORY")
DYNAMODB_SERVICE = os.getenv("DYNAMODB_SERVICE")
TABLE_NAME = os.getenv("TABLE_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")
AWS_REGION = os.getenv("REGION")
AWS_ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")

S3_SERVICE = os.getenv("S3_SERVICE")
INPUT_BUCKET_NAME = os.getenv("INPUT_CEPH_BUCKET_NAME")
OUTPUT_BUCKET_NAME = os.getenv("OUTPUT_CEPH_BUCKET_NAME")
OUTPUT_S3_FILE_LOCATION = os.getenv("S3_LOCATION").format(OUTPUT_BUCKET_NAME)
CEPH_ACCESSKEY_ID = os.getenv("CEPH_ACCESSKEY_ID")
CEPH_SECRETKEY_ID = os.getenv("CEPH_SECRETKEY_ID")
CEPH_ENDPOINT_URL = os.getenv("CEPH_ENDPOINT_URL")

s3Client = boto3.client(
    S3_SERVICE,
    aws_access_key_id=CEPH_ACCESSKEY_ID,
    aws_secret_access_key=CEPH_SECRETKEY_ID,
    endpoint_url=CEPH_ENDPOINT_URL
)

dynamodbClient = boto3.resource(
    DYNAMODB_SERVICE,
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def downloadVideoFromS3ToLocal(key):
    if not os.path.exists(INPUT_LOCAL_STORAGE_DIR):
        os.makedirs(INPUT_LOCAL_STORAGE_DIR)
    try:
        localPath = os.path.join(INPUT_LOCAL_STORAGE_DIR, key)
        s3Client.download_file(
            INPUT_BUCKET_NAME,
            key,
            localPath
        )
    except Exception as exception:
        print("Exception in downloading file to local", exception)
        return exception
    return localPath

def addResultObjectToS3(imageName):
    filepath = OUTPUT_FILE_DIRECTORY + '/' + imageName + '.csv'
    try:
        s3Client.upload_file(filepath, OUTPUT_BUCKET_NAME, imageName + '.csv')
    except Exception as exception:
        print("Exception in uploading result from App Instance", exception)
        return exception
    return "{}{}".format(OUTPUT_S3_FILE_LOCATION, imageName)

def queryTable(resultName):
    table = dynamodbClient.Table(TABLE_NAME)
    response = table.query(
        IndexName=INDEX_NAME,
        KeyConditionExpression=Key('name').eq(resultName)
    )
    print(response['Items'])
    if response['Items'][0]: return response['Items'][0]

def writeResultToCsv(data, filename):
    if not os.path.exists(OUTPUT_FILE_DIRECTORY):
        os.makedirs(OUTPUT_FILE_DIRECTORY)
    filepath = OUTPUT_FILE_DIRECTORY + '/' + filename
    name = data.get('name', '')
    major = data.get('major', '')
    year = data.get('year', '')
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, major, year])

def extract_frames(videoPath):
	if not os.path.exists(INPUT_FRAME_STORAGE_DIR):
		os.makedirs(INPUT_FRAME_STORAGE_DIR)
	os.system("ffmpeg -i " + str(videoPath) + " -r 1 " + str(INPUT_FRAME_STORAGE_DIR) + "image-%3d.jpeg")

# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def compare_image_with_embeddings(framePath, encodingData):
	frame = face_recognition.load_image_file(framePath)
	frameEncodings = face_recognition.face_encodings(frame)
	resultName = ''
	faceRecognized = False
	if len(frameEncodings) == 0:
		return faceRecognized, resultName
	else:
		frameEncoding = frameEncodings[0]
		results = face_recognition.compare_faces(encodingData['encoding'], frameEncoding)
		resultIndex = np.argmax(results)
		resultName = encodingData['name'][resultIndex]
		faceRecognized = True
		return faceRecognized, resultName

def handle(event, context):
	#eventInput = json.dumps(event.body)
	#eventJson = json.loads(eventInput)
	print(event)
	objectKey = event['key']
	videoPath = downloadVideoFromS3ToLocal(objectKey)
	videoName = os.path.basename(videoPath)
	extract_frames(videoPath)
	encodingData = open_encoding(ENCODING_PATH)
	frames = os.listdir(INPUT_FRAME_STORAGE_DIR)
	resultName = ''
	for frame in frames:
		faceRecognized, resultName = compare_image_with_embeddings(os.path.join(INPUT_FRAME_STORAGE_DIR, frame), encodingData)
		if faceRecognized:
			break
	print(videoName, resultName)
	resultFromDynamoDb = queryTable(resultName)
	if resultFromDynamoDb:
		writeResultToCsv(resultFromDynamoDb, videoName.split('.')[0] + '.csv')
		addResultObjectToS3(videoName.split('.')[0])
	else:
		print("Error getting details from dynamodb for " + resultName)