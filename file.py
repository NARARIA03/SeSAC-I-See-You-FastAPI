from fastapi import APIRouter
from fastapi.responses import FileResponse

fileRouter = APIRouter()


@fileRouter.get("/mp3/image/{fileName}")
async def getMp3File(fileName: int) -> FileResponse:
    path = f"./mp3/image/{fileName}.mp3"
    return FileResponse(path, media_type="audio/mpeg")


@fileRouter.get("/mp3/voice/{fileName}")
async def getMp3File(fileName: int) -> FileResponse:
    path = f"./mp3/voice/{fileName}.mp3"
    return FileResponse(path, media_type="audio/mpeg")
