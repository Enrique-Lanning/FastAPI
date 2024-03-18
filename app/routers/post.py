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
    prefix="/posts",
    tags=['Posts']
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

@router.get("/", response_model=List[schemas.ResponseGetPosts])
def get_posts():
    mycursor.execute("SELECT posts.*, COUNT(votes.post_id) AS votes, users.email FROM posts LEFT OUTER JOIN votes ON posts.id = votes.post_id LEFT OUTER JOIN users ON posts.user_ident = users.id GROUP BY posts.id;")
    posts = mycursor.fetchall()
    mydb.commit()
    
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not retrieve posts.")
    
    response_posts = []
    for post in posts:
        response_post = schemas.ResponseGetPosts(
            title=post[1],
            content=post[2],
            published=post[3],
            created_at=post[4],
            user_ident=post[5],
            email=post[7],
            votes=post[6]
        )
        response_posts.append(response_post)
    
    return response_posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ResponseCreateUserInfo)
def create_post(post: schemas.PostCreateUpdate, current_user: int = Depends(oauth2.get_current_user)):
    sql = "INSERT INTO posts (Title, Content, Published, User_ident) VALUES (%s, %s, %s, %s);" 
    val = (post.title, post.content, post.published, current_user[1])
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.execute("SELECT title, content, published, user_ident FROM posts ORDER BY id DESC LIMIT 1")
    new_post = mycursor.fetchone()
    mydb.commit()
    mycursor.execute("SELECT email FROM users WHERE id = %s", (current_user[1], ))
    user_info = mycursor.fetchone()
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")
    return schemas.ResponseCreateUserInfo(title=new_post[0], content=new_post[1], published=new_post[2], user_ident=new_post[3], user_info=user_info[0])

@router.get("/{id}", response_model=schemas.ResponseSinglePostUpdate)
def get_post(id: int, response: Response):
    mycursor.execute("SELECT title, content, published, user_ident FROM posts WHERE id = %s", (str(id), ))
    id_post = mycursor.fetchone()
    mydb.commit()
    print(id_post)
    if not id_post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found.')
    return schemas.ResponseSinglePostUpdate(title=id_post[0], content=id_post[1], published=id_post[2], user_ident=id_post[3])

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, current_user: int = Depends(oauth2.get_current_user)):
    mycursor.execute("SELECT * FROM posts WHERE id = %s", (str(id), ))
    deleted_post = mycursor.fetchone()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} does not exist.")
    if deleted_post[5] != current_user[1]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to perform requested action.")
    mycursor.execute("DELETE FROM posts WHERE id = %s", (str(id), ))
    mydb.commit()
    print(f"{deleted_post} successfully deleted.")
    return deleted_post

@router.put("/{id}", response_model=schemas.ResponseSinglePostUpdate)
def update_post(id: int, post: schemas.PostCreateUpdate, current_user: int = Depends(oauth2.get_current_user)):
    mycursor.execute("UPDATE posts SET Title = %s, Content = %s, Published = %s WHERE id = %s", (post.title, post.content, post.published, str(id)))
    mydb.commit()
    mycursor.execute("SELECT title, content, published, user_ident FROM posts WHERE id = %s", (str(id), ))
    updated_post = mycursor.fetchone()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if updated_post[3] != current_user[1]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to perform requested action.")
    mydb.commit()
    return schemas.ResponseSinglePostUpdate(title=updated_post[0], content=updated_post[1], published=updated_post[2], user_ident=updated_post[3])

