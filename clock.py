from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pytz

from models import User, Log, Base
from database import Session, engine
from config import TZ
import utils

sched = BlockingScheduler(tz=TZ)

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=7) # run every weekday at 7:00am
def processingDataJob():
    s = Session()

    Base.metadata.bind = engine
    Course = Base.metadata.tables['courses']
    Course.drop(engine)
    Course.create(engine)

    users = s.query(User).all()
    utils.processingData(users, s)
    
    print('Data has been succesfully collected')
    # utils.newLog('clock.py', 'Data has been succesfully collected', s)


    s.close()

sched.start()

# @sched.scheduled_job('interval', minutes=3)
# def processingDataJob():

#     s = Session()

#     Base.metadata.bind = engine
#     Course = Base.metadata.tables['courses']
#     Course.drop(engine)
#     Course.create(engine)

#     users = s.query(User).all()
#     utils.processingData(users, s)
    
#     print("Data has been successfully collected")

#     s.close()

if __name__ == '__main__':
    processingDataJob()
