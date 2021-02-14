
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

def processingData(users: int, s: Session, td: int = 0):
    
    accepted_keys = ['SUMMARY;LANGUAGE=fr', 'LOCATION;LANGUAGE=fr', 'DTSTART', 'DTEND']
    data = {}
    
    for user in users:
        
        data['courses'] = jicson.fromWeb(user.url, auth="")["VCALENDAR\r"][0]["VEVENT\r"]
        df = pd.json_normalize(data['courses'])
        unaccepted_keys = [header for header in df.columns.values if not header in accepted_keys]    
        df = df.drop(columns=unaccepted_keys)
        df.columns = [x.split(";")[0].lower() for x in df.columns]
        
        df['dtstart'] = pd.to_datetime(df.dtstart).dt.tz_convert(None) + pd.Timedelta(1, unit='h')
        df['dtend'] = pd.to_datetime(df.dtend).dt.tz_convert(None) + pd.Timedelta(1, unit='h')

        ts  = pd.to_datetime(datetime.now(tz=tz.gettz(TZ))) + pd.Timedelta(td, unit='days')
    
        df = df.loc[(df.dtstart.dt.date == ts.date()), :]
        df.sort_values(by='dtstart', ascending = True, inplace = True)

        df['dtstart'] = df.dtstart.dt.strftime('%Y-%m-%d %H:%M:%S')
        df['dtend'] = df.dtend.dt.strftime('%Y-%m-%d %H:%M:%S')
        df['location'].fillna('No specified location', inplace=True)

        data = df.to_json(orient='table', index=False)
        data = json.loads(data)['data']

        for elem in data:
            course = models.Course(dtstart=elem['dtstart'], dtend=elem['dtend'], summary=elem['summary'], location=elem['location'], user_id=user.id)
            s.add(course)

        s.commit()



def getNextCourse(user_id: int, popped: bool, s: Session) -> models.Course:
    now = datetime.now(tz=tz.gettz(TZ))
    course = s.query(models.Course).filter(models.Course.user_id==user_id, models.Course.dtstart >= now).order_by(models.Course.dtstart.asc()).limit(1).first()
    if popped and course is not None:
        s.delete(course)
        s.commit()
        return course
    else:
        return course
    
def getNextCourses(user_id: int, s: Session) -> List[models.Course]:
    courses = s.query(models.Course).filter_by(user_id=user_id).all()
    if len(courses) > 1:
        return courses
    else:
        return None

def getUser(user_id: int, s: Session) -> models.User:   
    user = s.query(models.User).filter_by(id=user_id).first()
    if user is  not None:
        return user
    else:
        return None


def getCourses(s: Session) -> List[models.Course]:
    return s.query(models.Course).all()

def getUsers(s: Session) -> List[models.User]:
    return s.query(models.User).all()



def create_user(user: schemas.UserCreate, s: Session) -> models.User:
    if user.preferences is not None:
        user_preferences = json.dumps(user.preferences)
    else:
        user_preferences = user.preferences
    user = models.User(id=user.id, first_name=user.first_name, last_name=user.last_name, url=user.url, preferences=user.preferences)
    s.add(user)
    s.commit()
    return user

def update_preferences(update: schemas.UserUpdate, s: Session) -> models.User:
    s.query(models.User).filter_by(id=update.user_id).update({models.User.preferences: json.dumps(update.preferences)})
    s.commit()
    return getUser(update.user_id, s)

if __name__ == '__main__':
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