from fastapi import FastAPI
from imageRouter import imageRouter
from file import fileRouter

app = FastAPI()
app.include_router(imageRouter)
app.include_router(fileRouter)


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}
