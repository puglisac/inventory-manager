import os

S3_BUCKET                 = os.environ.get("S3_BUCKET_NAME", "fake_name")
S3_KEY                    = os.environ.get("S3_ACCESS_KEY", "fake_key")
S3_SECRET                 = os.environ.get("S3_SECRET_ACCESS_KEY", "fake_secret")
S3_LOCATION               = f'http://{S3_BUCKET}.s3.amazonaws.com/'
