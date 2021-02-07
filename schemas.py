from typing import Optional, List, Union
from pydantic import BaseModel, HttpUrl
from datetime import datetime

import models

class CourseBase(BaseModel):
    dtstart: datetime
    dtend: datetime
    summary: str

class Course(CourseBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    name: str
    preferences: Optional[Union[dict, str]]

class UserCreate(UserBase):
    url: HttpUrl

class User(UserBase):
    id: int
    courses: List[Course]

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    user_id: int
    preferences: dict