import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=True)

class Episode(Base):
    __tablename__ = "episodes"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    episode_text = Column(Text)
    guide_script = Column(Text)
    student_script = Column(Text)
    dialogue = Column(JSON) # Storing list of DialogueTurn objects
    word_count = Column(Integer)
    language = Column(String)
    model = Column(String)
    episode_dir = Column(String)
    guidance_audio = Column(JSON) # Storing Dict[Voice, str]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(String, ForeignKey("episodes.id"))
    rating = Column(Integer)
    platform = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    episode = relationship("Episode", back_populates="feedback")

Episode.feedback = relationship("Feedback", order_by=Feedback.id, back_populates="episode")
