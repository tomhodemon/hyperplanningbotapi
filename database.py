import sys
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from models import Base
from config import DATABASE_URL

engine = sqlalchemy.create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

if __name__ == '__main__':

    from models import User
    from config import URL

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    s = Session()
    user = {
        "chat_id" : 1227641700,
        "first_name" : "Tom",
        "last_name" : "Hodemon",
        "url": URL        
    }
    user = User(**user)
    s.add(user)
    s.commit()
    s.close()
