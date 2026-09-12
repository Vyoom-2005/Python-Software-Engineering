from .models import Student,Instructor,Course,Enrollment
from .exceptions import *
from .storage import JSONStorage,CSVStorage
class Registrar:
 def __init__(self): self.students={};self.instructors={};self.courses={};self.enrollments=[]
 def add_student(self,x):
  if x.person_id in self.students or x.person_id in self.instructors: raise DuplicateRecordError(x.person_id)
  self.students[x.person_id]=x
 def add_instructor(self,x):
  if x.person_id in self.students or x.person_id in self.instructors: raise DuplicateRecordError(x.person_id)
  self.instructors[x.person_id]=x
 def add_course(self,x):
  if x.course_id in self.courses: raise DuplicateRecordError(x.course_id)
  self.courses[x.course_id]=x
 def enroll(self,s,c):
  if s not in self.students: raise RecordNotFoundError(s)
  if c not in self.courses: raise RecordNotFoundError(c)
  e=Enrollment(s,c)
  if e in self.enrollments: raise EnrollmentError('already enrolled')
  self.enrollments.append(e);return e
 def drop(self,s,c):
  try:self.enrollments.remove(Enrollment(s,c))
  except ValueError as e:raise EnrollmentError('enrollment does not exist') from e
 def get_student_courses(self,s):
  if s not in self.students: raise RecordNotFoundError(s)
  ids={e.course_id for e in self.enrollments if e.student_id==s};return [self.courses[i] for i in sorted(ids)]
 def people_display(self): return [x.display_name() for x in list(self.students.values())+list(self.instructors.values())]
 def to_dict(self): return {"students":[self.students[k].to_dict() for k in sorted(self.students)],"instructors":[self.instructors[k].to_dict() for k in sorted(self.instructors)],"courses":[self.courses[k].to_dict() for k in sorted(self.courses)],"enrollments":[e.to_dict() for e in sorted(self.enrollments,key=lambda x:(x.student_id,x.course_id))]}
 def save_json(self,p):JSONStorage.save(p,self.to_dict())
 def save_csv(self,p):CSVStorage.save(p,self.to_dict())
 @classmethod
 def load_json(c,p):return c._from_dict(JSONStorage.load(p))
 @classmethod
 def load_csv(c,p):return c._from_dict(CSVStorage.load(p))
 @classmethod
 def _from_dict(c,d):
  r=c()
  for x in d['students']:r.add_student(Student(x['person_id'],x['name'],x['email'],x['program']))
  for x in d['instructors']:r.add_instructor(Instructor(x['person_id'],x['name'],x['email'],x['department']))
  for x in d['courses']:r.add_course(Course(x['course_id'],x['title'],int(x['credits'])))
  for x in d['enrollments']:r.enroll(x['student_id'],x['course_id'])
  return r
