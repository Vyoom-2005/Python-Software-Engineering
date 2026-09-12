from fastapi import FastAPI,Depends,HTTPException,status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .database import Base,engine,get_db
from .models import User,Note
from .schemas import *
from .security import hash_password,verify_password,create_token
from .auth import current_user
Base.metadata.create_all(engine)
app=FastAPI(title='Secure Notes Microservice',version='1.0.0',description='FastAPI REST API with Pydantic validation, SQLite persistence, bcrypt password hashing and JWT Bearer authentication.')
@app.get('/health',tags=['system'])
def health(): return {'status':'ok'}
@app.post('/register',response_model=UserPublic,status_code=201,tags=['authentication'])
def register(x:UserCreate,db:Session=Depends(get_db)):
    email=str(x.email).lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,'Email is already registered')
    u=User(email=email,password_hash=hash_password(x.password)); db.add(u)
    try: db.commit(); db.refresh(u)
    except IntegrityError: db.rollback(); raise HTTPException(409,'Email is already registered')
    return u
@app.post('/login',response_model=Token,tags=['authentication'])
def login(x:UserCreate,db:Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.email==str(x.email).lower()))
    if not u or not verify_password(x.password,u.password_hash): raise HTTPException(401,'Invalid email or password',headers={'WWW-Authenticate':'Bearer'})
    return Token(access_token=create_token(u.id))
@app.get('/me',response_model=UserPublic,tags=['users'])
def me(u=Depends(current_user)): return u
def owned(nid,uid,db):
    n=db.scalar(select(Note).where(Note.id==nid,Note.owner_id==uid))
    if not n: raise HTTPException(404,'Note not found')
    return n
@app.post('/notes',response_model=NotePublic,status_code=201,tags=['notes'])
def create_note(x:NoteCreate,u=Depends(current_user),db:Session=Depends(get_db)):
    n=Note(title=x.title.strip(),content=x.content.strip(),owner_id=u.id)
    if not n.title or not n.content: raise HTTPException(422,'Title and content cannot be blank')
    db.add(n);db.commit();db.refresh(n);return n
@app.get('/notes',response_model=list[NotePublic],tags=['notes'])
def list_notes(u=Depends(current_user),db:Session=Depends(get_db)): return list(db.scalars(select(Note).where(Note.owner_id==u.id).order_by(Note.id)))
@app.get('/notes/{nid}',response_model=NotePublic,tags=['notes'])
def get_note(nid:int,u=Depends(current_user),db:Session=Depends(get_db)): return owned(nid,u.id,db)
@app.put('/notes/{nid}',response_model=NotePublic,tags=['notes'])
def update_note(nid:int,x:NoteUpdate,u=Depends(current_user),db:Session=Depends(get_db)):
    n=owned(nid,u.id,db); d=x.model_dump(exclude_unset=True)
    if 'title' in d:n.title=d['title'].strip()
    if 'content' in d:n.content=d['content'].strip()
    if not n.title or not n.content:raise HTTPException(422,'Title and content cannot be blank')
    db.commit();db.refresh(n);return n
@app.delete('/notes/{nid}',status_code=204,tags=['notes'])
def delete_note(nid:int,u=Depends(current_user),db:Session=Depends(get_db)):
    db.delete(owned(nid,u.id,db));db.commit()
