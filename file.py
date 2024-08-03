from fastapi import APIRouter
from fastapi.responses import FileResponse

fileRouter = APIRouter()


@fileRouter.get("/mp3/{fileName}")
async def getMp3File(fileName: int) -> FileResponse:
    path = f"./mp3/{fileName}.mp3"
    return FileResponse(path, media_type="audio/mpeg")
