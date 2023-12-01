import boto3


# Set your Ceph credentials and endpoint
ceph_access_key = 'diyaaccesskey'
ceph_secret_key = 'diyasecretkey'
ceph_endpoint_url = 'http://192.168.64.9:8000'  # Replace with your Ceph cluster endpoint


# Create a Ceph S3 client
s3 = boto3.client('s3', aws_access_key_id=ceph_access_key, aws_secret_access_key=ceph_secret_key, endpoint_url=ceph_endpoint_url)


# List all buckets
try:
   response = s3.list_objects_v2(Bucket="image-classification-input")
   for obj in response.get('Contents', []):
       print(f"Object: {obj['Key']}, Size: {obj['Size']} bytes")
except Exception as e:
   print(f"Error: {e}")
