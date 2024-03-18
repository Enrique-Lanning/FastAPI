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
    prefix="/vote",
    tags=["Vote"]
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

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, current_user: int = Depends(oauth2.get_current_user)):
    mycursor.execute("SELECT title, content, published, user_ident FROM posts WHERE id = %s", (str(vote.post_id), ))
    post = mycursor.fetchone()
    mydb.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {vote.post_id} does not exist")
    mycursor.execute("SELECT post_id, user_id FROM votes WHERE post_id = %s AND user_id = %s", (str(vote.post_id), str(current_user[1]), ))
    vote_query = mycursor.fetchone()
    mydb.commit()
    if (vote.dir == True):
        if vote_query:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User {current_user[1]} has already voted on post {vote.post_id}")
        sql = "INSERT INTO votes (post_id, user_id) VALUES (%s, %s);" 
        val = (vote.post_id, current_user[1])
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.execute("SELECT post_id, user_id FROM votes WHERE post_id = %s AND user_id = %s", (str(vote.post_id), str(current_user[1]), ))
        new_vote = mycursor.fetchone()
        mydb.commit()
        return {"message": "successfully added vote"}
    else:
        if not vote_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist")
        mycursor.execute("DELETE FROM votes WHERE post_id = %s", (str(vote.post_id), ))
        mydb.commit()
        return {"message": "successfully deleted vote"}
        

