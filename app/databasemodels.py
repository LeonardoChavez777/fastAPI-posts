from .database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Boolean, text
from sqlalchemy.orm import relationship



class Post(Base):
    __tablename__ = "posts"
    
    Id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE',
                       nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False,
                        server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey("users.Id", ondelete="CASCADE"), nullable=False)  # Foreign key to the users table
    owner = relationship("User")
    

    
class User(Base):
    __tablename__ = "users"

    Id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False,
                        server_default=text('now()'))
    

class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey("users.Id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.Id", ondelete="CASCADE"), primary_key=True)