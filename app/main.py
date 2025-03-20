from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.authorization import authorization_router
from .routers.feed import feed_router

app: FastAPI = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authorization_router)
app.include_router(feed_router)
