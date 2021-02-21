"""
[] MIGRATE TO DOCKER
[] ERROR GESTURE PROCESSINGDATA
"""

from typing import List, Union
from datetime import datetime
from fastapi import FastAPI, Depends

from database import engine, Session
import utils
import schemas

app = FastAPI()

def getSession():
    s = Session()
    try:
        yield s
    finally:
        s.close()
    
@app.get("/user/{user_id}/nextcourse", response_model=Union[schemas.Course, None])
def nextcourse(user_id: int, popped: bool=False, s: Session=Depends(getSession)):
    nextcourse = utils.getNextCourse(user_id, popped, s)
    return nextcourse

@app.get("/user/{user_id}/nextcourses", response_model=Union[List[schemas.Course], None])
def nextcourses(user_id: int, s: Session=Depends(getSession)):
    nextcourses = utils.getNextCourses(user_id, s)
    return nextcourses

@app.post("/user/create", response_model=schemas.User)
def create_user(user: schemas.UserCreate, s: Session = Depends(getSession)):
    user = utils.create_user(user, s)
    return user

@app.post("/user/update", response_model=schemas.User)
def update_preferences(update: schemas.UserUpdate, s: Session = Depends(getSession)):
    """
    updates preferences column of an user
    """
    user = utils.update_preferences(update, s)
    return user

@app.get("/user/{user_id}", response_model=schemas.User)
def user(user_id: int, s: Session=Depends(getSession)):
    """
    returns the user object whose id has been passed in parameter
    """
    user = utils.getUser(user_id, s)
    return user



@app.get("/")
def index():
    """
    index endpoint
    """
    return "Welcome to HYPERPLANNINGBOTAPI"

@app.get("/admin/users", response_model=List[schemas.User])
def users(s: Session=Depends(getSession)):
    """
    returns a list containing all user objects
    """
    users = utils.getUsers(s)
    return users

@app.get("/admin/courses", response_model=List[schemas.Course])
def courses(s: Session=Depends(getSession)):
    """
    returns a list containing all course objects
    """
    courses = utils.getCourses(s)
    return courses

@app.get("/admin/logs", response_model=List[schemas.Log])
def logs(sender: str=None, today: bool=False, s: Session=Depends(getSession)):
    logs = utils.getLogs(sender, today, s)
    return logs