import os
import s3 as s3Util
import dynamodb as dynamodbUtil
import face_recognition
import pickle
import numpy as np
import csvUtil
import json

INPUT_BUCKET_NAME = os.getenv("INPUT_S3_BUCKET_NAME")
INPUT_LOCAL_STORAGE_DIR = os.getenv("INPUT_LOCAL_STORAGE_DIR")
INPUT_FRAME_STORAGE_DIR = os.getenv("INPUT_FRAME_STORAGE_DIR")
ENCODING_PATH = os.getenv("ENCODING_PATH")

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
	videoPath = s3Util.downloadVideoFromS3ToLocal(objectKey)
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
	resultFromDynamoDb = dynamodbUtil.queryTable(resultName)
	if resultFromDynamoDb:
		csvUtil.writeResultToCsv(resultFromDynamoDb, videoName.split('.')[0] + '.csv')
		s3Util.addResultObjectToS3(videoName.split('.')[0])
	else:
		print("Error getting details from dynamodb for " + resultName)