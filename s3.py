
import boto3, botocore
from config import S3_KEY, S3_LOCATION, S3_SECRET, S3_BUCKET

s3 = boto3.resource(
    "s3",
    aws_access_key_id=S3_KEY, 
    aws_secret_access_key=S3_SECRET
)

bucket = s3.Bucket(S3_BUCKET)


def upload_file_to_s3(file, filename):

    try:
        read_file=file.read()
        bucket.Object(filename).put(Body=read_file)

    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    return f"{S3_LOCATION}{filename}"

def delete_file_from_s3(file_url):
    try:
        filename_arr=file_url.split("/")
        filename=filename_arr[len(filename_arr)-1]
        bucket.Object(filename).delete()
    
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e