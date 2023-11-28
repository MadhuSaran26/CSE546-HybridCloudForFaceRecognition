import boto3
import requests
import time

# Ceph S3 configuration
ceph_access_key = 'diyaaccesskey'
ceph_secret_key = 'diyasecretkey'
ceph_endpoint_url = 'http://192.168.64.9:8000'

# OpenFaaS configuration
openfaas_function_url = 'http://openfaas-gateway/function/your-function'

# Bucket to monitor
bucket_name = 'image-classification-input'

# Initialize S3 client
s3 = boto3.client('s3', aws_access_key_id=ceph_access_key, aws_secret_access_key=ceph_secret_key, endpoint_url=ceph_endpoint_url)

# Keep track of processed objects
processed_objects = set()

def monitor_input():
    while True:
        # List objects in the bucket
        response = s3.list_objects(Bucket=bucket_name)

        for obj in response.get('Contents', []):
            object_key = obj['Key']

            # Check if the object is new
            if object_key not in processed_objects:
                # Trigger OpenFaaS function
                #requests.post(openfaas_function_url, json={'object_key': object_key})
                print(object_key)

                # Add the object to the processed set
                processed_objects.add(object_key)

    # Sleep for some time before checking again
        time.sleep(10)