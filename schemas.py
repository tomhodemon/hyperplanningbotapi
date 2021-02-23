from typing import Optional, List, Union
from pydantic import BaseModel, HttpUrl
from datetime import datetime

import models

###### Course ######
class Course(BaseModel):
    id: int
    user_id: int
    tz: str
    dtstart: datetime
    dtend: datetime
    summary: str
    location: str

    class Config:
        orm_mode = True   

###### User ######
class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    preferences: Optional[Union[dict]]
    courses: Optional[List[Course]] = []
    url: HttpUrl

    class Config:
        orm_mode = True

class UserCreate(User):
    pass

class UserUpdate(BaseModel):
    user_id: int
    preferences: dict

###### Log ######
class Log(BaseModel):
    id: int
    tz: str
    dt: datetime
    sender: str
    log: str

    class Config:
        orm_mode = True