from fastapi import FastAPI, Response, HTTPException, Depends, status, APIRouter
from fastapi.params import Body
import mysql.connector
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import time
from app import schemas, utils, oauth2
from ..config import settings

router = APIRouter(
    tags=['Authentication']
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
        break
    except Exception as error:
        print("Connecting to database failed.")
        print("Error: ", error)
        time.sleep(3)

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin):
    mycursor.execute("SELECT id, email, password FROM users WHERE email = %s", (user_credentials.email,) )
    login_creds = mycursor.fetchone()
    mydb.commit()
    if not login_creds:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials.")
    
    if not utils.verify(user_credentials.password, login_creds[2]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials.")
    
    access_token = oauth2.create_access_token(data = {"user_id": login_creds[0]})
    return {"access_token": access_token, "token_type": "bearer"}
