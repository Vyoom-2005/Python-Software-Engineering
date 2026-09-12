import csv,json
from pathlib import Path
from .exceptions import StorageError
KEYS={"students","instructors","courses","enrollments"}
class JSONStorage:
 @staticmethod
 def save(path,data):
  try: Path(path).parent.mkdir(parents=True,exist_ok=True); Path(path).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf8')
  except Exception as e: raise StorageError(str(e))
 @staticmethod
 def load(path):
  try: data=json.loads(Path(path).read_text(encoding='utf8'))
  except FileNotFoundError as e: raise StorageError('JSON file not found') from e
  except Exception as e: raise StorageError('invalid JSON') from e
  if not isinstance(data,dict) or set(data)!=KEYS or not all(isinstance(data[k],list) for k in KEYS): raise StorageError('invalid JSON structure')
  return data
class CSVStorage:
 F={"students":("students.csv",["person_id","name","email","program"]),"instructors":("instructors.csv",["person_id","name","email","department"]),"courses":("courses.csv",["course_id","title","credits"]),"enrollments":("enrollments.csv",["student_id","course_id"])}
 @classmethod
 def save(c,d,data):
  try:
   p=Path(d);p.mkdir(parents=True,exist_ok=True)
   for k,(fn,fields) in c.F.items():
    with (p/fn).open('w',newline='',encoding='utf8') as f: w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(data[k])
  except Exception as e: raise StorageError(str(e))
 @classmethod
 def load(c,d):
  out={}
  try:
   for k,(fn,fields) in c.F.items():
    with (Path(d)/fn).open(newline='',encoding='utf8') as f: out[k]=list(csv.DictReader(f))
  except Exception as e: raise StorageError(str(e))
  return out
