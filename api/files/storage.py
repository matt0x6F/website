from storages.backends.s3boto3 import S3Boto3Storage

from core.config import get_config

config = get_config()


class PublicStorage(S3Boto3Storage):
    access_key = config.s3.access_key_id
    secret_key = config.s3.secret_access_key
    bucket_name = config.s3.bucket_name
    region_name = config.s3.region
    default_acl = "public-read"
    endpoint_url = config.s3.endpoint_url
    file_overwrite = False
    custom_domain = config.s3.cdn_endpoint
    location = config.s3.prefix


class PrivateStorage(S3Boto3Storage):
    access_key = config.s3.access_key_id
    secret_key = config.s3.secret_access_key
    bucket_name = config.s3.bucket_name
    region_name = config.s3.region
    default_acl = "private"
    endpoint_url = config.s3.endpoint_url
    file_overwrite = False
    custom_domain = config.s3.cdn_endpoint
    location = config.s3.prefix
