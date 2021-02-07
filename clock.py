from apscheduler.schedulers.blocking import BlockingScheduler

from models import User, Base
from database import Session, engine
import utils

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=7) # run every weekday at 7:00am
def processingDataJob():

    s = Session()

    Base.metadata.bind = engine
    Course = Base.metadata.tables['courses']
    Course.drop(engine)
    Course.create(engine)

    users = s.query(User).filter(User.name != 'Admin').all()
    utils.processingData(users, s)

    s.close()

sched.start()

# if __name__ == '__main__':
#     processingDataJob()
