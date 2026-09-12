import unittest,tempfile,json
from pathlib import Path
from data_engine.models import *
from data_engine.registrar import Registrar
from data_engine.exceptions import *
class Tests(unittest.TestCase):
 def setUp(self):
  self.r=Registrar();self.r.add_student(Student('S1','Alice','alice@example.com','BCA'));self.r.add_instructor(Instructor('I1','Bob','bob@example.com','CS'));self.r.add_course(Course('C1','Python',4))
 def test_oop(self): self.assertEqual(self.r.people_display(),['Student: Alice','Instructor: Bob'])
 def test_validation(self):
  with self.assertRaises(ValidationError):Student('S','','bad','')
  with self.assertRaises(ValidationError):Course('C','X',0)
 def test_duplicate(self):
  with self.assertRaises(DuplicateRecordError):self.r.add_student(Student('S1','X','x@x.com','BCA'))
 def test_enrollment(self): self.r.enroll('S1','C1');self.assertEqual(self.r.get_student_courses('S1')[0].course_id,'C1')
 def test_bad_enrollment(self):
  with self.assertRaises(RecordNotFoundError):self.r.enroll('X','C1')
 def test_duplicate_drop(self):
  self.r.enroll('S1','C1')
  with self.assertRaises(EnrollmentError):self.r.enroll('S1','C1')
  self.r.drop('S1','C1')
  with self.assertRaises(EnrollmentError):self.r.drop('S1','C1')
 def test_json_csv(self):
  with tempfile.TemporaryDirectory() as d:
   j=Path(d)/'r.json';self.r.enroll('S1','C1');self.r.save_json(j);self.assertEqual(Registrar.load_json(j).to_dict(),self.r.to_dict());self.r.save_csv(d+'/csv');self.assertEqual(Registrar.load_csv(d+'/csv').to_dict(),self.r.to_dict())
 def test_bad_json(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.json';p.write_text('{bad')
   with self.assertRaises(StorageError):Registrar.load_json(p)
if __name__=='__main__':unittest.main()
