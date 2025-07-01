import enum
from sqlalchemy import (Column, Integer, String, Text, DateTime, ForeignKey, Enum)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class CrawlSource(Base):
    __tablename__ = 'crawl_sources'
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    last_crawled_at = Column(DateTime(timezone=True), server_default=func.now())

class BlogPost(Base):
    __tablename__ = 'blog_posts'
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    comments = relationship("Comment", back_populates="blog_post")

class CommentStatus(enum.Enum):
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    posted = "posted"

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    blog_post_id = Column(Integer, ForeignKey('blog_posts.id'), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String, default="KloudPortal Team")
    status = Column(Enum(CommentStatus), default=CommentStatus.pending_review, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    blog_post = relationship("BlogPost", back_populates="comments")
