from apscheduler.schedulers.blocking import BlockingScheduler

from models import User, Base
from database import Session, engine
import utils
#from config import TZ

# sched = BlockingScheduler(tz=TZ)
sched = BlockingScheduler()

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=7) # run every weekday at 7:00am
def processingDataJob():
    s = Session()

    Base.metadata.bind = engine
    Course = Base.metadata.tables['courses']
    Course.drop(engine)
    Course.create(engine)

    users = s.query(User).all()
    utils.processingData(users, s)
    
    print("Data has been successfully collected")

    s.close()

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

# sched.start()

if __name__ == '__main__':
    processingDataJob()
