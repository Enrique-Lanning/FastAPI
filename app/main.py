from fastapi import FastAPI, Response, HTTPException, Depends, status, APIRouter
from fastapi.params import Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import mysql.connector
import time
from . import schemas, utils, oauth2
from . routers import post, user, authentication, vote
from .config import settings

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

while True:

    try:
        mydb = mysql.connector.connect(
            host=f"{settings.database_hostname}",
            user=f"{settings.database_username}",
            password=f"{settings.database_password}",
            database=f"{settings.database_name}"
        )
        mycursor = mydb.cursor()
        print("Database connection was successful.")
        break
    except Exception as error:
        print("Connecting to database failed.")
        print("Error: ", error)
        time.sleep(3)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(oauth2.router)
app.include_router(vote.router)