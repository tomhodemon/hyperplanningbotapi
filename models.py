from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    url = Column(String)
    preferences = Column(JSON, nullable=True)

    courses = relationship('Course', backref='user')

    def __repr__(self):
        return "User(id={}, chat_id={}, first_name='{}', last_name='{}', preferences={}, courses={})"\
                .format(self.id, self.chat_id, self.first_name, self.last_name, self.preferences, self.courses)

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    dtstart = Column(DateTime)
    dtend = Column(DateTime)
    summary = Column(String)
    location = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return "Course(id={}, dtstart={}, dtend={}, summary='{}', location='{}', user_id={})"\
                .format(self.id, self.dtstart, self.dtend, self.summary, self.location, self.user_id)

