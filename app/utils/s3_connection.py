from contextlib import asynccontextmanager
from aiobotocore.session import get_session

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
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=f"test/{file_path.split("\\")[-1]}",
                    Body=file,
                )

    async def download_file(
            self,
            file_path: str,
    ):
        async with self.get_client() as client:
            response = await client.get_object(
                Bucket=self.bucket_name,
                Key=file_path,
            )
            
        return response["Body"]
    
    async def delete_file(
            self,
            file_path: str,
    ):
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path,
            )
