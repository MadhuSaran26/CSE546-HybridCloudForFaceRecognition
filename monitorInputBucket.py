import boto3
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

# Ceph S3 configuration
CEPH_ACCESSKEY_ID = os.getenv("CEPH_ACCESSKEY_ID")
CEPH_SECRETKEY_ID = os.getenv("CEPH_SECRETKEY_ID")
CEPH_ENDPOINT_URL = os.getenv("CEPH_ENDPOINT_URL")

# OpenFaaS configuration
OPENFAAS_FUNCTION_URL = 'http://127.0.0.1:8080/function/face-recog'

# Bucket to monitor
S3_SERVICE = os.getenv("S3_SERVICE")
INPUT_BUCKET_NAME = os.getenv("INPUT_CEPH_BUCKET_NAME")

# Initialize S3 client
s3Client = boto3.client(S3_SERVICE, aws_access_key_id=CEPH_ACCESSKEY_ID, 
                  aws_secret_access_key=CEPH_SECRETKEY_ID, endpoint_url=CEPH_ENDPOINT_URL)

# Keep track of processed objects
processedObjects = set()

def monitor_input():
    while True:
        # List objects in the bucket
        response = s3Client.list_objects(Bucket=INPUT_BUCKET_NAME)

        for obj in response.get('Contents', []):
            objectKey = obj['Key']

            # Check if the object is new
            if objectKey not in processedObjects:
                # Trigger OpenFaaS function
                #requests.post(openfaas_function_url, json={'object_key': object_key})
                print(f"New video detected: {objectKey}")

                #videoUrl = f"{CEPH_ENDPOINT_URL}/{INPUT_BUCKET_NAME}/{objectKey}"
                
                payload = {"key": objectKey}
                headers = {"Content-Type": "application/json"}
                
                response = requests.post(OPENFAAS_FUNCTION_URL, json=payload, headers=headers)
                
                if response.status_code == 200:
                    print("Function invoked successfully.")
                else:
                    print(f"Error invoking function. Status code: {response.status_code}")

                # Add the object to the processed set
                processedObjects.add(objectKey)

    # Sleep for some time before checking again
        time.sleep(10)
# if __name__ == "__main__":
#     monitor_input()