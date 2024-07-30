from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from imageRouter import imageRouter
from voiceRouter import voiceRouter
from file import fileRouter

app = FastAPI()
app.include_router(imageRouter)
app.include_router(fileRouter)
app.include_router(voiceRouter)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}
