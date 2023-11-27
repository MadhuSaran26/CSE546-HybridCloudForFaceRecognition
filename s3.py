import boto3
import boto
import boto.s3.connection
import os
from dotenv import load_dotenv
load_dotenv()

S3_SERVICE = os.getenv("S3_SERVICE")
INPUT_BUCKET_NAME = os.getenv("INPUT_S3_BUCKET_NAME")
INPUT_S3_FILE_LOCATION = os.getenv("S3_LOCATION").format(INPUT_BUCKET_NAME)
OUTPUT_BUCKET_NAME = os.getenv("OUTPUT_S3_BUCKET_NAME")
OUTPUT_S3_FILE_LOCATION = os.getenv("S3_LOCATION").format(OUTPUT_BUCKET_NAME)
INPUT_LOCAL_STORAGE_DIR = os.getenv("INPUT_LOCAL_STORAGE_DIR")
INPUT_FRAME_STORAGE_DIR = os.getenv("INPUT_FRAME_STORAGE_DIR")
OUTPUT_FILE_DIRECTORY = os.getenv("OUTPUT_FILE_DIRECTORY")
AWS_ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
s3Client = boto3.client(
    S3_SERVICE,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
conn = boto.connect_s3(
    aws_access_key_id="diyaaccesskey",
    aws_secret_access_key="diyasecretkey",
    host='https://192.168.64.8:8000',
    is_secure=False,               # uncomment if you are not using ssl
    calling_format=boto.s3.connection.OrdinaryCallingFormat()
)
for bucket in conn.get_all_buckets():
        print("{name}\t{created}".format(
                name = bucket.name,
                created = bucket.creation_date,
        ))
def creates3InputBucket():
    conn.create_bucket("test-bucket")
    print("Creating bucket")

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
#creates3InputBucket()