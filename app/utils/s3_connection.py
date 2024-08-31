from contextlib import asynccontextmanager
import os
from aiobotocore.session import get_session
import aiofiles

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
            file_path: str,
    ) -> None:
        async with self.get_client() as client:
            with open(file_path, "rb") as file:
                k = file_path.split('\\')[-1] # no need in python3.12 for some reason
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=f"test/{k}",
                    Body=file,
                )

    async def download_file(
            self,
            file_path: str,
    ) -> str | None:
        folder_path = "storage"
        file_name = file_path.split("/")[-1]

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        local_file_path = os.path.join(folder_path, file_name)

        try:
            async with self.get_client() as client:
                response = await client.get_object(
                    Bucket=self.bucket_name,
                    Key=file_path,
                )

                async with response['Body'] as stream:
                    async with aiofiles.open(local_file_path, 'wb') as file:
                        await file.write(await stream.read())
        except:
            return None
        
        return local_file_path
            
    
    async def delete_file(
            self,
            file_path: str,
    ):
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path,
            )


    def cleanup(self, file_path: str):
        os.remove(file_path)
