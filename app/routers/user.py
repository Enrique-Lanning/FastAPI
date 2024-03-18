from fastapi import FastAPI, Response, HTTPException, Depends, status, APIRouter
from fastapi.params import Body
import mysql.connector
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import time
from .. import schemas, utils, oauth2
from ..config import settings

router = APIRouter(
    prefix="/users",
    tags=['Users']
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

@router.post("/", status_code=status.HTTP_201_CREATED,  response_model=schemas.ResponseUser)
def create_user(user: schemas.UserCreate):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    sql = "INSERT INTO users (email, password) VALUES (%s, %s);" 
    val = (user.email, user.password)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.execute("SELECT id, email, created_at FROM users ORDER BY id DESC LIMIT 1")
    new_user = mycursor.fetchone()
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")
    return schemas.ResponseUser(id=new_user[0], email=new_user[1], created_at=new_user[2])

@router.get('/{id}', response_model=schemas.ResponseUser)
def get_user(id: int):
    mycursor.execute("SELECT id, email, created_at FROM users WHERE id = %s", (str(id), ))
    get_user = mycursor.fetchone()
    mydb.commit()
    if not get_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID: {id} does not exist.")
    return schemas.ResponseUser(id=get_user[0], email=get_user[1], created_at=get_user[2])
