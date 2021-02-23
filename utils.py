
from sqlalchemy.orm.session import Session
from sqlalchemy import func
from typing import List
import jicson
import json
from dateutil import tz
from datetime import datetime, timedelta, time, date
import pandas as pd
import pytz

import models
from config import URL, TZ, TZ_OBJECT
import schemas

def processingData(users: int, s: Session, td: int = 0):
    
    accepted_keys = ['SUMMARY;LANGUAGE=fr', 'LOCATION;LANGUAGE=fr', 'DTSTART', 'DTEND']
    data = {}
    
    for user in users:
        
        data['courses'] = jicson.fromWeb(user.url, auth="")["VCALENDAR\r"][0]["VEVENT\r"]

        # dev.
        # with open('data.json', 'r') as file:
        #     d = json.load(file)
        #     data['courses'] = d["VEVENT\r"]

        df = pd.json_normalize(data['courses'])


        unaccepted_keys = [header for header in df.columns.values if not header in accepted_keys]    
        df = df.drop(columns=unaccepted_keys)
        df.columns = [x.split(";")[0].lower() for x in df.columns]
        df.replace({r'\r': ''}, regex=True, inplace=True)

        # dev.
        # df['dtstart'] = pd.to_datetime(df.dtstart).dt.tz_convert(None) + pd.Timedelta(1, unit='h')
        # df['dtend'] = pd.to_datetime(df.dtend).dt.tz_convert(None) + pd.Timedelta(1, unit='h')
        # df['dtstart'] = pd.to_datetime(df.dtstart).dt.tz_convert(TZ_OBJECT)
        # df['dtend'] = pd.to_datetime(df.dtend).dt.tz_convert(TZ_OBJECT)

        df['dtstart'] = pd.to_datetime(df.dtstart)
        df['dtend'] = pd.to_datetime(df.dtend)

        ts  = pd.to_datetime(datetime.now(tz=pytz.utc)) + pd.Timedelta(td, unit='days')
       
        df = df.loc[(df.dtstart.dt.date == ts.date()), :]
        df.sort_values(by='dtstart', ascending = True, inplace = True)

        df['location'].fillna('No specified location', inplace=True)

        data = df.to_json(orient='table', index=False)
        data = json.loads(data)['data']

        print(len(data))
        for elem in data:
            # elem = slotProcessing(elem)
            course = models.Course(dtstart=elem['dtstart'], dtend=elem['dtend'], summary=elem['summary'], location=elem['location'], user_id=user.id)
            s.add(course)
        
        # s.commit()

def slotProcessing(course: dict) -> dict:

    slots = {
        "type": "standard",
        "tz": "UTC",
        "slot1": {
            "dtstart": "07:00:00",
            "dtend": "08:20:00"
        },
        "slot2": {
            "dtstart": "08:35:00",
            "dtend": "09:55:00"
        },
        "slot3": {
            "dtstart": "10:05:00",
            "dtend": "11:25:00"
        },
        "slot4": {
            "dtstart": "12:50:00",
            "dtend": "14:10:00"
        },
        "slot5": {
            "dtstart": "14:20:00",
            "dtend": "15:40:00"
        },
        "slot6": {
            "dtstart": "15:55:00",
            "dtend": "17:15:00"
        }
    }

    ctype = course['summary'].replace('\r', '').replace(' ', '').split('-')[-1]
    if ctype == 'TD':
        course['ctype'] = 'standard'
    else:
        course['ctype'] = 'special'
    print('sum: ', course, 'ctype: ', ctype)
    return course
    


def getNextCourse(user_id: int, popped: bool, s: Session) -> models.Course:
    now = datetime.now(tz=tz.gettz(TZ))
    course = s.query(models.Course).filter(models.Course.user_id==user_id, models.Course.dtstart >= now).order_by(models.Course.dtstart.asc()).limit(1).first()
    if course is not None:
        if popped:
            s.delete(course)
            s.commit()
            print('popped course')
            return course
        else:
            return course
    else:
        return None
    
def getNextCourses(user_id: int, s: Session) -> List[models.Course]:
    courses = s.query(models.Course).filter_by(user_id=user_id).all()
    if len(courses) >= 1:
        return courses
    else:
        return None

def create_user(user: schemas.UserCreate, s: Session) -> models.User:
    user_preferences = {}
    user_preferences['AutoMessaging'] = False

    user = models.User(id=user.id, first_name=user.first_name, last_name=user.last_name, url=user.url, preferences=user_preferences)
    s.add(user)
    s.commit()
    return user

def getUser(user_id: int, s: Session) -> models.User:   
    user = s.query(models.User).filter_by(id=user_id).first()
    if user is not None:
        return user
    else:
        return None

def getCourses(s: Session) -> List[models.Course]:
    return s.query(models.Course).all()

def getUsers(s: Session) -> List[models.User]:
    return s.query(models.User).all()


def update_preferences(update: schemas.UserUpdate, s: Session) -> models.User:
    s.query(models.User).filter_by(id=update.user_id).update({models.User.preferences: json.dumps(update.preferences)})
    s.commit()
    return getUser(update.user_id, s)

def getLogs(sender: str, today: bool, s: Session) -> List[models.Log]:
    if today:
        now = datetime.now(tz=TZ_OBJECT).date()
        if sender:
            logs = s.query(models.Log).filter(models.Log.sender == sender, func.date(models.Log.dt) == now).limit(50).all()
        else:
            logs = s.query(models.Log).filter(func.date(models.Log.dt) == now).limit(50).all()
    else:
        if sender:
            logs = s.query(models.Log).filter_by(sender=sender).limit(50).all()
        else:
            logs = s.query(models.Log).limit(50).all()
    if len(logs) >= 1:
        return logs
    else: 
        return None

# def newLog(sender: str, message: str, s: Session):
#     log = models.Log(dt=datetime.now(tz=pytz.utc), sender=sender, log=message)
#     s.add(log)
#     s.commit()   
#     s.close()

if __name__ == '__main__':
    # dev.
    # url = "https://tomorrow.audencia.com/public/api/courses/1bd232472374f44a8ecc92a709c946fb.ics"
    # data = jicson.fromWeb(url, auth="")['VCALENDAR'][0]['VEVENT']
    # with open('data.json', 'w') as file:
    #     json.dump(data, file, indent=2)
    # df = pd.json_normalize(data)
    # print(df.head(10))

    from database import Session
    from models import User
    import sys

    if len(sys.argv) > 1:
        td = int(sys.argv[1]) #timedelta
    else:
        td = 0

    s = Session()

    users = s.query(User).all()

    processingData(users, s, td)

    s.close()