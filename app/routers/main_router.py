from pathlib import Path
from typing import Annotated
import aiofiles
from fastapi import APIRouter, BackgroundTasks, Depends, Form
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastui import AnyComponent, FastUI, components as c, prebuilt_html

from app.models.user import User, get_current_active_user
from app.utils.s3_connection import S3Client
from app.utils.extension_mapping import MEDIA_TYPES


router = APIRouter()
s3_client = S3Client(
    "L201GGN3PARM2UOEH46F",
    "Qk1rldX0xI3nPgncA8awr7DYAIjqA1jezkYf2rIo",
    "http://91.222.131.165:8080",
    "uecloud",
)


@router.get("/api/", response_class=FastUI, response_model_exclude_none=True)
async def get_index(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[AnyComponent]:
    #index_path = Path("frontend/index.html")
    #return index_path.read_text(encoding="utf-8")

    return [
        c.Page(
            components=[
                c.Heading(text='Home', level='1'),
            ]
        )
    ]


@router.post("/upload/")
async def post_upload(
    path: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    await s3_client.upload_file(path)


@router.post("/download/")
async def post_download(
    path: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_active_user)],
    back: BackgroundTasks,
):
    local_file_path = await s3_client.download_file(path)

    if not local_file_path:
        return
    
    extension = local_file_path.split("/")[-1].split(".")[-1]

    back.add_task(s3_client.cleanup, local_file_path)
    
    return FileResponse(local_file_path, media_type=MEDIA_TYPES.get(extension), background=back)


@router.post("/delete/")
async def post_delete(
    path: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    await s3_client.delete_file(path)


# @router.get("/users/me/", response_model=User)
# async def read_users_me(
#     current_user: Annotated[User, Depends(get_current_active_user)],
# ):
#     return current_user

@router.get("/api/users/me/", response_class=FastUI, response_model_exclude_none=True)
def get_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                c.Heading(text=current_user.username, level=2),
                c.Paragraph(text=f'email: {current_user.email}'),
                c.Paragraph(text=f'telegram: {current_user.telegram}'),
            ],
        ),
    ]

@router.get('/{path:path}')
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='UECloud'))