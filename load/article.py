from sqlalchemy import Column, String, Integer
from base import Base

class Article(Base):
    __tablename__ = 'articles'

    id = Column(String, primary_key=True)
    title = Column(String)
    body = Column(String)
    newspaper_uid = Column(String)
    n_tokens_title = Column(Integer)
    n_tokens_body = Column(Integer)
    host = Column(String)
    url = Column(String, unique=True)
    origin = Column(String)

    def __init__(self, uid, title, body, newspaper_uid, n_tokens_title, n_tokens_body, host, url, origin) -> None:
        self.id = uid
        self.title = title
        self.body = body
        self.newspaper_uid = newspaper_uid
        self.n_tokens_title = n_tokens_title
        self.n_tokens_body = n_tokens_body
        self.host = host
        self.url = url
        self.origin = origin