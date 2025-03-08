from boib.filesystems import Filesystem

import aioboto3
from aiofiles import os


class S3Filesystem(Filesystem): 
     
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region_name: str | None = None,
        endpoint_url: str | None = None,
        prefix: str = '',
    ):
            self.__bucket_name = bucket_name
            self.__aws_access_key_id = aws_access_key_id
            self.__aws_secret_access_key = aws_secret_access_key
            self.__region_name = region_name
            self.__endpoint_url = endpoint_url
            self.__prefix = prefix.rstrip('/') + '/' if prefix else ''

    async def write(self, path: str, bytes):
        session = aioboto3.Session(
            aws_access_key_id=self.__aws_access_key_id,
            aws_secret_access_key=self.__aws_secret_access_key,
            region_name=self.__region_name,
        )

        full_path = os.path.join(self.__prefix, path)
        
        async with session.client('s3', endpoint_url=self.__endpoint_url) as s3:
            await s3.put_object(
                Bucket=self.__bucket_name,
                Key=full_path,
                Body=bytes,
            )
