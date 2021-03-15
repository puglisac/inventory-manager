
import boto3, botocore
from config import S3_KEY, S3_SECRET, S3_BUCKET

s3 = boto3.resource(
    "s3",
    aws_access_key_id=S3_KEY, 
    aws_secret_access_key=S3_SECRET
)

bucket = s3.Bucket(S3_BUCKET)


def upload_file_to_s3(file, filename, bucket_name=S3_BUCKET, acl="public-read"):

    try:
        read_file=file.read()
        bucket.Object(filename).put(Body=read_file)

    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    return f"https://amys-costume-shop-photos.s3.amazonaws.com/{filename}"

    