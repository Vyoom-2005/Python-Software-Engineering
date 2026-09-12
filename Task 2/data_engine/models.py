import re
from dataclasses import dataclass
from .exceptions import ValidationError

def req(v, f):
    if not isinstance(v,str) or not v.strip(): raise ValidationError(f"{f} must be non-empty")
    return v.strip()
def ident(v,f): return req(v,f)
class Person:
    role="person"
    def __init__(self,person_id,name,email): self.person_id=ident(person_id,"person_id"); self.name=req(name,"name"); self.email=email
    @property
    def email(self): return self._email
    @email.setter
    def email(self,v):
        v=req(v,"email")
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$',v): raise ValidationError("invalid email")
        self._email=v.lower()
    def display_name(self): return self.name
    def to_dict(self): return {"person_id":self.person_id,"name":self.name,"email":self.email,"role":self.role}
class Student(Person):
    role="student"
    def __init__(self,p,n,e,program): super().__init__(p,n,e); self.program=req(program,"program")
    def display_name(self): return f"Student: {self.name}"
    def to_dict(self): return {**super().to_dict(),"program":self.program}
class Instructor(Person):
    role="instructor"
    def __init__(self,p,n,e,department): super().__init__(p,n,e); self.department=req(department,"department")
    def display_name(self): return f"Instructor: {self.name}"
    def to_dict(self): return {**super().to_dict(),"department":self.department}
@dataclass(frozen=True)
class Course:
    course_id:str; title:str; credits:int
    def __post_init__(self):
        object.__setattr__(self,"course_id",ident(self.course_id,"course_id")); object.__setattr__(self,"title",req(self.title,"title"))
        if not isinstance(self.credits,int) or not 1<=self.credits<=10: raise ValidationError("credits must be 1-10")
    def to_dict(self): return {"course_id":self.course_id,"title":self.title,"credits":self.credits}
@dataclass(frozen=True)
class Enrollment:
    student_id:str; course_id:str
    def __post_init__(self): object.__setattr__(self,"student_id",ident(self.student_id,"student_id")); object.__setattr__(self,"course_id",ident(self.course_id,"course_id"))
    def to_dict(self): return {"student_id":self.student_id,"course_id":self.course_id}
