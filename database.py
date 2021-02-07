import sys
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from models import Base
from config import DATABASE_URL

engine = sqlalchemy.create_engine(DATABASE_URL)

print('database import')

Session = sessionmaker(bind=engine)

if __name__ == '__main__':

    from models import User
    from config import URL

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    s = Session()
    user = User(name='Tom Hodemon', url=URL)
    s.add(user)
    s.commit()
    s.close()
