from fastapi import FastAPI, Response, HTTPException, Depends, status, APIRouter
from fastapi.params import Body
import mysql.connector
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ResponseGetPosts(BaseModel):
    title: str
    content: str
    published: bool = True
    created_at: datetime
    user_ident: int
    email: str
    votes: int

class PostCreateUpdate(BaseModel):
    title: str
    content: str
    published: bool = True

class ResponseCreateUserInfo(BaseModel):
    title: str
    content: str
    published: bool = True
    user_ident: int
    user_info: str

class ResponseSinglePostUpdate(BaseModel):
    title: str
    content: str
    published: bool = True
    user_ident: int

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class ResponseUser(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

class Vote(BaseModel):
    post_id: int
    dir: bool