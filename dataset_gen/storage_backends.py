from storages.backends.s3boto3 import S3Boto3Storage

class DatasetsStorage(S3Boto3Storage):
    location = 'datasets'
    file_overwrite = False