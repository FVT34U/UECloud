from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.utils.exception_handler import http_exception_handler
from app.routers.main_router import router as MainRouter
from app.routers.auth_router import router as AuthRouter
from app.routers.users_router import router as UsersRouter
from app.routers.storage_router import router as StorageRouter


app = FastAPI(
    root_path="/api"
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.include_router(MainRouter)
app.include_router(AuthRouter)
app.include_router(UsersRouter)
app.include_router(StorageRouter)
app.add_exception_handler(HTTPException, http_exception_handler)


origins = [
    "https://localhost:5173",
    "https://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    pass

if __name__ == '__main__':
    main()