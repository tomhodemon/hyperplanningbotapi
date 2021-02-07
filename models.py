from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    preferences = Column(String, nullable=True)

    courses = relationship('Course', backref='user')

    def __repr__(self):
        return "User(id={}, name='{}', preferences={}, courses={})"\
                .format(self.id, self.name, self.preferences, self.courses)

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    dtstart = Column(DateTime)
    dtend = Column(DateTime)
    summary = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return "Course(id={}, dtstart={}, dtend={}, summary='{}', user_id={})"\
                .format(self.id, self.dtstart, self.dtend, self.summary, self.user_id)

