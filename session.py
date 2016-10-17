from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import MYSQL_DB_NAME, MYSQL_HOST, MYSQL_PASS, MYSQL_USER
from models import Base

engine = create_engine('mysql+pymysql://' + MYSQL_USER + ':' +
                       MYSQL_PASS + '@' + MYSQL_HOST + '/' +
                       MYSQL_DB_NAME + "?charset=utf8", pool_recycle=3600)
Base.metadata.create_all(engine)
Sess = sessionmaker(bind=engine, expire_on_commit=False, autocommit=False)


class Session(object):

    def __init__(self):
        self.session = Sess()

    def __enter__(self):
        return self.session

    def __exit__(self, *exception):
        if exception[0] is not None:
            self.session.rollback()
        self.session.close()