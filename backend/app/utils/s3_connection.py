from contextlib import asynccontextmanager
import os
import uuid
from aiobotocore.session import get_session
import aiofiles
from fastapi import UploadFile

from app.utils.make_zip import zip_directory

class S3Client:

    """ 
    s3 client connection class \n
    methods:
        upload_file
        download_file
        delete_file
    """

    def __init__(self,
                 access_key: str,
                 secret_key: str,
                 endpoint_url: str,
                 bucket_name: str,
    ) -> None:
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(
            self,
            file: bytes,
            file_path: str,
    ) -> None:
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file,
            )

    async def download_file(
            self,
            file_path: str,
            file_type: str,
    ) -> str | None:
        temp_folder_name = str(uuid.uuid4())
        temp_storage_path = f"storage/{temp_folder_name}"
        local_file_path = ''
        orig_file_name = file_path.split("/")[-1]

        print('filepath', file_path)

        try:
            async with self.get_client() as client:
                paginator = client.get_paginator('list_objects_v2')
                async for result in paginator.paginate(Bucket=self.bucket_name, Prefix=file_path):
                    if 'Contents' in result:
                        for obj in result['Contents']:
                            key = obj['Key']

                            response = await client.get_object(
                                Bucket=self.bucket_name,
                                Key=key,
                            )

                            print(key) # по ключу короче сохранять данные, там файлы в основном

                            local_folder = ''
                            local_file = ''

                            if file_type != 'file':
                                local_folder = f"{temp_storage_path}/{"/".join(file_path.split('/')[0:-1])}"
                                local_file = f"{temp_storage_path}/{file_path}"
                            else:
                                local_folder = temp_storage_path
                                local_file = f"{temp_storage_path}/{orig_file_name}"
                            
                            os.makedirs(local_folder, exist_ok=True)

                            async with response['Body'] as stream:
                                async with aiofiles.open(local_file, 'wb') as file:
                                    await file.write(await stream.read())
                
                if file_type != 'file':
                    zip_directory(temp_storage_path)
                    return f"{temp_storage_path}/{temp_folder_name}.zip", temp_folder_name
                else:
                    return f"{temp_storage_path}/{orig_file_name}", temp_folder_name
    
        except Exception as ex:
            print(ex)
            return None
            
    
    async def delete_file(
            self,
            file_path: str,
    ):
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path,
            )

    
    async def create_dir(
        self,
        path: str,
    ) -> None:
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=f"{path}/stashkeep.stashkeep",
                Body=b'',
            )


    def cleanup(self, file_path: str):
        os.remove(file_path)


s3_client = S3Client(
    "L201GGN3PARM2UOEH46F",
    "Qk1rldX0xI3nPgncA8awr7DYAIjqA1jezkYf2rIo",
    "http://91.222.131.165:8080",
    "uecloud",
)
