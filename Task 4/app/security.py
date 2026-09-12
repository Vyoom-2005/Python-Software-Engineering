import os,base64,hashlib,hmac,json
try:
    import bcrypt
except ImportError:
    bcrypt=None
try:
    import jwt
except ImportError:
    jwt=None
from datetime import datetime,timedelta,timezone
from fastapi import HTTPException,status
SECRET=os.getenv('JWT_SECRET','development-secret-change-this-to-a-32-byte-secret'); ALG='HS256'; MINUTES=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES','60'))
def hash_password(p):
    if bcrypt is not None: return bcrypt.hashpw(p.encode(),bcrypt.gensalt()).decode()
    salt=os.urandom(16); digest=hashlib.scrypt(p.encode(),salt=salt,n=2**14,r=8,p=1).hex(); return 'fallback$'+base64.urlsafe_b64encode(salt).decode()+'$'+digest
def verify_password(p,h):
    try:
        if bcrypt is not None and h.startswith('$2'): return bcrypt.checkpw(p.encode(),h.encode())
        if h.startswith('fallback$'):
            _,salt,digest=h.split('$',2); return hmac.compare_digest(hashlib.scrypt(p.encode(),salt=base64.urlsafe_b64decode(salt),n=2**14,r=8,p=1).hex(),digest)
        return False
    except (ValueError,TypeError): return False
def _b64(x): return base64.urlsafe_b64encode(x).rstrip(b'=').decode()
def create_token(uid):
    now=datetime.now(timezone.utc); payload={'sub':str(uid),'iat':int(now.timestamp()),'exp':int((now+timedelta(minutes=MINUTES)).timestamp())}
    if jwt is not None: return jwt.encode(payload,SECRET,algorithm=ALG)
    head=_b64(b'{"alg":"HS256","typ":"JWT"}'); body=_b64(json.dumps(payload,separators=(',',':')).encode()); sig=_b64(hmac.new(SECRET.encode(),(head+'.'+body).encode(),hashlib.sha256).digest()); return head+'.'+body+'.'+sig
def decode_token(t):
    err=HTTPException(status_code=401,detail='Invalid or expired access token',headers={'WWW-Authenticate':'Bearer'})
    try:
        if jwt is not None: uid=int(jwt.decode(t,SECRET,algorithms=[ALG]).get('sub'))
        else:
            head,body,sig=t.split('.'); expected=_b64(hmac.new(SECRET.encode(),(head+'.'+body).encode(),hashlib.sha256).digest())
            if not hmac.compare_digest(sig,expected): raise ValueError
            data=json.loads(base64.urlsafe_b64decode(body+'='*((4-len(body)%4)%4)));
            if int(data.get('exp',0)) < int(datetime.now(timezone.utc).timestamp()): raise ValueError
            uid=int(data.get('sub'))
        if uid<1: raise ValueError
        return uid
    except Exception: raise err
