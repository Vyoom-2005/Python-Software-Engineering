from sqlalchemy import ForeignKey,String,Text
from sqlalchemy.orm import Mapped,mapped_column,relationship
from .database import Base
class User(Base):
    __tablename__='users'; id:Mapped[int]=mapped_column(primary_key=True); email:Mapped[str]=mapped_column(String(320),unique=True,index=True); password_hash:Mapped[str]=mapped_column(String(255)); notes:Mapped[list['Note']]=relationship(back_populates='owner',cascade='all, delete-orphan')
class Note(Base):
    __tablename__='notes'; id:Mapped[int]=mapped_column(primary_key=True); title:Mapped[str]=mapped_column(String(120)); content:Mapped[str]=mapped_column(Text); owner_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True); owner:Mapped[User]=relationship(back_populates='notes')
