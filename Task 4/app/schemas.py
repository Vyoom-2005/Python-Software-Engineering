from pydantic import BaseModel,ConfigDict,EmailStr,Field
class UserCreate(BaseModel): email:EmailStr; password:str=Field(min_length=8,max_length=128)
class UserPublic(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; email:EmailStr
class Token(BaseModel): access_token:str; token_type:str='bearer'
class NoteCreate(BaseModel): title:str=Field(min_length=1,max_length=120); content:str=Field(min_length=1,max_length=5000)
class NoteUpdate(BaseModel): title:str|None=Field(default=None,min_length=1,max_length=120); content:str|None=Field(default=None,min_length=1,max_length=5000)
class NotePublic(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; title:str; content:str; owner_id:int
