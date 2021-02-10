
from sqlalchemy.orm.session import Session
from typing import Dict, List
import jicson
import json
from dateutil import tz
from datetime import datetime, timedelta, time
import pandas as pd

import models
from config import URL, TZ
import schemas

def processingData(users: int, s: Session):
    
    accepted_keys = ['SUMMARY;LANGUAGE=fr', 'LOCATION;LANGUAGE=fr', 'DTSTART', 'DTEND']
    data = {}
    
    for user in users:
        
        data['courses'] = jicson.fromWeb(user.url, auth="")["VCALENDAR\r"][0]["VEVENT\r"]

        df = pd.json_normalize(data['courses'])

        unaccepted_keys = [header for header in df.columns.values if not header in accepted_keys]    
        df = df.drop(columns=unaccepted_keys)

        df.columns = [x.split(";")[0].lower() for x in df.columns]
      
        df['dtstart'] = pd.to_datetime(df['dtstart']).dt.tz_convert(TZ)
        df['dtend'] = pd.to_datetime(df['dtend']).dt.tz_convert(TZ)
        
        df = df.set_index('dtstart')

        today_start = datetime.now(tz=tz.gettz(TZ))\
                .replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now(tz=tz.gettz(TZ))\
                .replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        # today_start = datetime.now(tz=tz.gettz('Europe/Paris'))\
        #         .replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=3)
        # today_end = datetime.now(tz=tz.gettz('Europe/Paris'))\
        #         .replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=2)

        df = df.loc[today_start.strftime('%Y-%m-%d %H:%M:%S'):today_end.strftime('%Y-%m-%d %H:%M:%S')]
    
        df = df.sort_index()
        df = df.reset_index()
        
        print(df)
        
        data = df.to_json(orient='table', index=False)
        data = json.loads(data)['data']

        for elem in data:
            course = models.Course(dtstart=elem['dtstart'], dtend=elem['dtend'], summary=elem['summary'], location=elem['location'], user_id=user.id)
            s.add(course)

        s.commit()

def getNextCourse(user_id: int, popped: bool, s: Session) -> models.Course:
    now = datetime.now(tz=tz.gettz(TZ))
    course = s.query(models.Course).filter(models.Course.user_id==user_id, models.Course.dtstart > now).order_by(models.Course.dtstart.asc()).limit(1).first()
    if popped and course is not None:
        s.delete(course)
        s.commit()
        return course
    else:
        print('course is None (apperently)')
        return course
    
def getNextCourses(user_id: int, s: Session) -> List[models.Course]:
    return s.query(models.Course).filter_by(user_id=user_id).all()

def getCourses(s: Session) -> List[models.Course]:
    return s.query(models.Course).all()

def getUsers(s: Session) -> List[models.User]:
    return s.query(models.User).all()

def getUser(user_id: int, s: Session) -> models.User:   
    return s.query(models.User).filter_by(id=user_id).first()

def create_user(user: schemas.UserCreate, s: Session) -> models.User:
    if user.preferences is not None:
        user_preferences = json.dumps(user.preferences)
    else:
        user_preferences = user.preferences
    user = models.User(chat_id=user.chat_id, first_name=user.first_name, last_name=user.last_name, url=user.url, preferences=user.preferences)
    s.add(user)
    s.commit()
    return user

def update_preferences(update: schemas.UserUpdate, s: Session) -> models.User:
    s.query(models.User).filter_by(id=update.user_id).update({models.User.preferences: json.dumps(update.preferences)})
    s.commit()
    return getUser(update.user_id, s)
