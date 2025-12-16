from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    allergies = Column(String, nullable=True)

    parent_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    parent = relationship("User", back_populates="children")
