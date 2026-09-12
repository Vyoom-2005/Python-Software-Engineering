import os,tempfile
from pathlib import Path
T=tempfile.TemporaryDirectory();os.environ['DATABASE_URL']='sqlite:///'+str(Path(T.name)/'test.db');os.environ['JWT_SECRET']='test-secret'
from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def reg(e='a@example.com'):return c.post('/register',json={'email':e,'password':'StrongPass123'})
def tok(e='a@example.com'):return c.post('/login',json={'email':e,'password':'StrongPass123'}).json()['access_token']
def h(t):return {'Authorization':'Bearer '+t}
def test_health(): assert c.get('/health').json()=={'status':'ok'}
def test_register_duplicate(): assert reg().status_code==201;assert reg().status_code==409
def test_validation(): assert c.post('/register',json={'email':'bad','password':'short'}).status_code==422
def test_login_me(): assert c.get('/me',headers=h(tok())).status_code==200
def test_bad_login(): assert c.post('/login',json={'email':'a@example.com','password':'wrongpass'}).status_code==401
def test_protected(): assert c.get('/notes').status_code==401
def test_crud():
 t=tok();r=c.post('/notes',headers=h(t),json={'title':'Test','content':'Hello'});assert r.status_code==201;n=r.json()['id'];assert c.get('/notes/'+str(n),headers=h(t)).status_code==200;assert c.put('/notes/'+str(n),headers=h(t),json={'content':'Updated'}).json()['content']=='Updated';assert c.delete('/notes/'+str(n),headers=h(t)).status_code==204;assert c.get('/notes/'+str(n),headers=h(t)).status_code==404
def test_isolation():
 reg('b@example.com');bt=tok('b@example.com');n=c.post('/notes',headers=h(bt),json={'title':'private','content':'x'}).json()['id'];assert c.get('/notes/'+str(n),headers=h(tok())).status_code==404
