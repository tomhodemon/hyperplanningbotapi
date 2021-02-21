from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=False)
    first_name = Column(String)
    last_name = Column(String)
    url = Column(String)
    preferences = Column(JSON, nullable=True)

    courses = relationship('Course', backref='user')

    def __repr__(self):
        return "User(id={}, first_name='{}', last_name='{}', preferences={}, courses={})"\
                .format(self.id, self.first_name, self.last_name, self.preferences, self.courses)

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    tz = Column(String, default='UTC')
    dtstart = Column(DateTime(timezone=True))
    dtend = Column(DateTime(timezone=True))
    summary = Column(String)
    location = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return "Course(id={}, dtstart={}, dtend={}, summary='{}', location='{}', user_id={})"\
                .format(self.id, self.dtstart, self.dtend, self.summary, self.location, self.user_id)

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    tz = Column(String, default='UTC')
    dt = Column(DateTime(timezone=True))
    sender = Column(String)
    log = Column(String)

    def __repr__(self):
        return "Log(id={}, dt={}, sender='{}', log='{}')".format(self.id, self.dt, self.sender, self.log)
