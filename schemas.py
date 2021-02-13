from typing import Optional, List, Union
from pydantic import BaseModel, HttpUrl
from datetime import datetime

import models

class CourseBase(BaseModel):
    dtstart: datetime
    dtend: datetime
    summary: str
    location: Optional[str]

class Course(CourseBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    first_name: str
    last_name: str
    preferences: Optional[Union[dict, str]]
    courses: Optional[List[Course]]

class UserCreate(UserBase):
    id: int
    url: HttpUrl

class User(UserBase):
    id: int
    url: HttpUrl

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    user_id: int
    preferences: dict