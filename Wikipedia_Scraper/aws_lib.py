import datetime

import boto3
from botocore.exceptions import ClientError


def upload_file(file_name, bucket, object_key=None):
    """Upload a file to an S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_key: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_key was not specified, use file_name
    if object_key is not None:
        object_name = object_key
    else:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(f"Error uploading file {file_name} to bucket {bucket} object key {object_name}")
        return False
    return True


def upload_file_to_s3(fin):
    try:
        file_name = fin.rsplit('/', 1)[-1]
        curr_date = datetime.datetime.utcnow().strftime("%d-%m-%y_%H-%M")
        extension = file_name.split('.', 1)[-1]
        output_file_name = file_name.replace(f'.{extension}', f'-{curr_date}.{extension}')
        object_key = f"geojson/{output_file_name}"
        upload_file(fin, "outbreak-asia", object_key)
    except Exception as e:
        print(e)
