import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db

from schema import Course as SchemaCourse
from schema import Lesson as SchemaLesson
from schema import LResult as SchemaLResult
from schema import Mark as SchemaMark
from schema import Programme as SchemaProgramme
from schema import Status as SchemaStatus
from schema import StContract as SchemaStContract
from schema import Student as SchemaStudent
from schema import Teacher as SchemaTeacher
from schema import TeaContract as SchemaTeaContract
from schema import TeaStatus as SchemaTeaStatus
from schema import Timetable as SchemaTimetable


from schema import Course
from schema import Lesson
from schema import LResult
from schema import Mark
from schema import Programme 
from schema import Status 
from schema import StContract 
from schema import Student 
from schema import Teacher 
from schema import TeaContract 
from schema import TeaStatus 
from schema import Timetable 

from models import Course as ModelCourse
from models import Lesson as ModelLesson
from models import LResult as ModelLResult
from models import Mark as ModelMark
from models import Programme as ModelProgramme
from models import Status as ModelStatus
from models import StContract as ModelStContract
from models import Student as ModelStudent
from models import Teacher as ModelTeacher
from models import TeaContract as ModelTeaContract
from models import TeaStatus as ModelTeaStatus
from models import Timetable as ModelTimetable

import os
from dotenv import load_dotenv

load_dotenv('.env')


app = FastAPI()

# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])

@app.get("/")
async def root():
    return {"message": "hello world"}


@app.post('/student/', response_model=SchemaStudent)
async def student(student: SchemaStudent):
    db_student = ModelStudent(sname = student.sname, balance = student.balance)
    db.session.add(db_student)
    db.session.commit()
    return db_student

@app.get('/student/')
async def student():
    student = db.session.query(ModelStudent).all()
    return student

  
@app.post('/teacher/', response_model=SchemaTeacher)
async def teacher(teacher:SchemaTeacher):
    db_teacher = ModelTeacher(tname= teacher.tname, salary = teacher.salary)
    db.session.add(db_teacher)
    db.session.commit()
    return db_teacher

@app.get('/teacher/')
async def teacher():
    teacher = db.session.query(ModelTeacher).all()
    return teacher


# To run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)