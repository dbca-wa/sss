import os
import sys
import traceback
import boto3
import botocore

access_key = os.environ.get("S3_ACCESS_KEY")
secret_access_key = os.environ.get("S3_SECRET_ACCESS_KEY")
region = os.environ.get("S3_REGIONS") or "ap-southeast-2"
map_bucket_name = os.environ.get("GOKART_MAP_BUCKET")

exc_info = None
map_bucket = None

try:
    if not access_key or not secret_access_key: 
        raise Exception("Please configure S3 credential")

    if not map_bucket_name:
        raise Exception("Please configure gokart map bucket name")

    s3 = boto3.resource(
       's3',
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_access_key,
        region_name = region
    )

    try:
        s3.meta.client.head_bucket(Bucket=map_bucket_name)
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            raise Exception("The bucket({}) does not exist".format(map_bucket_name))


    map_bucket = s3.Bucket(map_bucket_name)
except :
    exc_info = sys.exc_info()
finally:
    if not map_bucket and not exc_info:
        try:
            raise Exception("Initialize s3 failed")
        except:
            exc_info = sys.exc_info()


def upload_map(bucket_key, filename, base_filename, content_type, meta):
    if not map_bucket:
        traceback.print_exception(*exc_info)
    else:
        try:
            with open(filename, 'rb') as f:
                map_bucket.Object(bucket_key).put(
                    Body = f,
                    ContentDisposition="attachment;filename={}".format(base_filename),
                    ContentType=content_type,
                    Metadata=meta
                )

        except:
           traceback.print_exc()

