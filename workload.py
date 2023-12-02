from boto3 import client as boto3_client
import boto3
import os
import requests
from dotenv import load_dotenv
#import monitorInputBucket
import threading
load_dotenv()

input_bucket = "image-classification-input"
output_bucket = "image-classification-output"
test_cases = "test_cases/"
S3_SERVICE = os.getenv("S3_SERVICE")
CEPH_ACCESSKEY_ID = os.getenv("CEPH_ACCESSKEY_ID")
CEPH_SECRETKEY_ID = os.getenv("CEPH_SECRETKEY_ID")
CEPH_ENDPOINT_URL = os.getenv("CEPH_ENDPOINT_URL")
OPENFAAS_FUNCTION_URL = 'http://127.0.0.1:8080/function/face-recognition-phttp'

def clear_input_bucket():
	global input_bucket
	s3 = boto3.client(
		S3_SERVICE,
		aws_access_key_id=CEPH_ACCESSKEY_ID,
		aws_secret_access_key=CEPH_SECRETKEY_ID,
		endpoint_url=CEPH_ENDPOINT_URL
	)

	list_obj = s3.list_objects_v2(Bucket=input_bucket)
	try:
		for item in list_obj["Contents"]:
			key = item["Key"]
			s3.delete_object(Bucket=input_bucket, Key=key)
	except:
		print("Nothing to clear in input bucket")
	
def clear_output_bucket():
	global output_bucket
	s3 = boto3.client(
		S3_SERVICE,
		aws_access_key_id=CEPH_ACCESSKEY_ID,
		aws_secret_access_key=CEPH_SECRETKEY_ID,
		endpoint_url=CEPH_ENDPOINT_URL
	)
	list_obj = s3.list_objects_v2(Bucket=output_bucket)
	try:
		for item in list_obj["Contents"]:
			key = item["Key"]
			s3.delete_object(Bucket=output_bucket, Key=key)
	except:
		print("Nothing to clear in output bucket")

def upload_to_input_bucket_s3(path, name):
	global input_bucket
	s3 = boto3.client(
		S3_SERVICE,
		aws_access_key_id=CEPH_ACCESSKEY_ID,
		aws_secret_access_key=CEPH_SECRETKEY_ID,
		endpoint_url=CEPH_ENDPOINT_URL
	)
	s3.upload_file(path + name, input_bucket, name)
	payload = {"key": name}
	headers = {"Content-Type": "application/json"}             
	response = requests.post(OPENFAAS_FUNCTION_URL, json=payload, headers=headers)
                
	if response.status_code == 200:
		print("Function invoked successfully.")
	else:
		print(f"Error invoking function. Status code: {response}")
	
	
def upload_files(test_case):	
	global input_bucket
	global output_bucket
	global test_cases
	
	
	# Directory of test case
	test_dir = test_cases + test_case + "/"
	
	# Iterate over each video
	# Upload to S3 input bucket
	for filename in os.listdir(test_dir):
		if filename.endswith(".mp4") or filename.endswith(".MP4"):
			print("Uploading to input bucket..  name: " + str(filename)) 
			upload_to_input_bucket_s3(test_dir, filename)
			
	
def workload_generator():
	
	print("Running Test Case 1")
	upload_files("test_case_1")

	# print("Running Test Case 2")
	# upload_files("test_case_2")

clear_input_bucket()
clear_output_bucket()
workload_generator()


	

