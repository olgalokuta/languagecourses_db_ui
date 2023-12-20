import uvicorn
from fastapi import FastAPI, Response, status
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

# student operations
@app.post('/student/', response_model=SchemaStudent)
async def createSt(student: SchemaStudent):
    db_student = ModelStudent(sname = student.sname, balance = student.balance)
    db.session.add(db_student)
    db.session.commit()
    db.session.refresh(db_student)
    return db_student

@app.get('/student/')
async def listSt():
    student = db.session.query(ModelStudent).all()
    return student

@app.get('/student/{id}')
async def readSt(id : int):
    student = db.session.query(ModelStudent).filter(ModelStudent.id_student == id)
    if student == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return student

@app.delete('/student/{id}')
async def deleteSt(id : int):
    del_student = db.session.query(ModelStudent).filter(ModelStudent.id_student == id)
    if del_student == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_student.delete(synchronize_session=False)
        db.session.commit()

@app.put('/student/{id}')
async def updateSt(id : int):
    upd_student = db.session.query(ModelStudent).filter(ModelStudent.id_student == id)
    if upd_student == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        upd_student.update(synchronize_session=False)
        db.session.commit()
        return upd_student

 # teacher operations 
@app.post('/teacher/', response_model=SchemaTeacher)
async def createT(teacher:SchemaTeacher):
    db_teacher = ModelTeacher(tname= teacher.tname, salary = teacher.salary)
    db.session.add(db_teacher)
    db.session.commit()
    return db_teacher

@app.get('/teacher/')
async def listT():
    teacher = db.session.query(ModelTeacher).all()
    return teacher

@app.get('/teacher/{id}')
async def readT(id : int):
    teacher = db.session.query(ModelTeacher).filter(ModelTeacher.id_teacher == id)
    if teacher == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return teacher

@app.delete('/teacher/{id}')
async def deleteT(id : int):
    del_teacher = db.session.query(ModelTeacher).filter(ModelTeacher.id_teacher == id)
    if del_teacher == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_teacher.delete(synchronize_session=False)
        db.session.commit()

@app.put('/teacher/{id}')
async def updateT(id : int):
    upd_teacher = db.session.query(ModelTeacher).filter(ModelTeacher.id_teacher == id)
    if upd_teacher == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        upd_teacher.update(synchronize_session=False)
        db.session.commit()
        return upd_teacher
    
# course operations
@app.post('/course/', response_model=SchemaCourse)
async def createC(course:SchemaCourse):
    db_course = ModelCourse(id_programme = course.id_programme, 
                            id_timetable = course.id_timetable, cdate = course.cdate)
    db.session.add(db_course)
    db.session.commit()
    return db_course

@app.get('/course/')
async def listC():
    course = db.session.query(ModelCourse).all()
    return course

@app.get('/course/{id}')
async def readC(id : int):
    course = db.session.query(ModelCourse).filter(ModelCourse.id_course == id)
    if course == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return course

@app.delete('/course/{id}')
async def deleteC(id : int):
    del_course = db.session.query(ModelCourse).filter(ModelCourse.id_course == id)
    if del_course == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_course.delete(synchronize_session=False)
        db.session.commit()

@app.put('/course/{id}')
async def updateC(id : int):
    upd_course = db.session.query(ModelCourse).filter(ModelCourse.id_course == id)
    if upd_course == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        upd_course.update(synchronize_session=False)
        db.session.commit()
        return upd_course
    
# mark operations
@app.post('/mark/', response_model=SchemaMark)
async def createM(mark: SchemaMark):
    db_mark = ModelMark(mark = mark.mark)
    db.session.add(db_mark)
    db.session.commit()
    db.session.refresh(db_mark)
    return db_mark

@app.get('/mark/')
async def listM():
    mark = db.session.query(ModelMark).all()
    return mark

@app.get('/mark/{id}')
async def readM(id : int):
    mark = db.session.query(ModelMark).filter(ModelMark.id_mark == id)
    if mark == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return mark

@app.delete('/mark/{id}')
async def deleteM(id : int):
    del_mark = db.session.query(ModelMark).filter(ModelMark.id_mark == id)
    if del_mark == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_mark.delete(synchronize_session=False)
        db.session.commit()

@app.put('/mark/{id}')
async def updateM(id : int):
    upd_mark = db.session.query(ModelMark).filter(ModelMark.id_mark == id)
    if upd_mark == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        upd_mark.update(synchronize_session=False)
        db.session.commit()
        return upd_mark
    
# status operations
@app.post('/status/', response_model=SchemaStatus)
async def createStat(status: SchemaStatus):
    db_status = ModelStatus(status = status.status)
    db.session.add(db_status)
    db.session.commit()
    db.session.refresh(db_status)
    return db_status

@app.get('/status/')
async def listStat():
    status = db.session.query(ModelStatus).all()
    return status

@app.get('/status/{id}')
async def readStat(id : int):
    stat = db.session.query(ModelStatus).filter(ModelStatus.id_status == id)
    if stat == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return stat

@app.delete('/status/{id}')
async def deleteStat(id : int):
    del_status = db.session.query(ModelStatus).filter(ModelStatus.id_status == id)
    if del_status == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_status.delete(synchronize_session=False)
        db.session.commit()

@app.put('/status/{id}')
async def updateStat(id : int):
    upd_status = db.session.query(ModelStatus).filter(ModelStatus.id_status == id)
    if upd_status == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        upd_status.update(synchronize_session=False)
        db.session.commit()
        return upd_status
    
# programme operations
@app.post('/programme/', response_model=SchemaProgramme)
async def createStat(prog: SchemaProgramme):
    db_prog= ModelProgramme(level = prog.level, intensity = prog.intensity,
                            book = prog.book, price = prog.price)
    db.session.add(db_prog)
    db.session.commit()
    db.session.refresh(db_prog)
    return db_prog

@app.get('/programme/')
async def listPr():
    prog = db.session.query(ModelProgramme).all()
    return prog

@app.get('/programme/{id}')
async def readPr(id : int):
    prog = db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id)
    if prog == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return prog

@app.delete('/programme/{id}')
async def deletePr(id : int):
    del_prog = db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id)
    if del_prog == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_prog.delete(synchronize_session=False)
        db.session.commit()

@app.put('/programme/{id}')
async def updatePr(id : int):
    upd_prog = db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id)
    if upd_prog == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        upd_prog.update(synchronize_session=False)
        db.session.commit()
        return upd_prog
    
# timetable operations
@app.post('/timetable/', response_model=SchemaTimetable)
async def createTT(tt: SchemaTimetable):
    db_tt = ModelTimetable(lessontime = tt.lessontime, weekday = tt.weekday)
    db.session.add(db_tt)
    db.session.commit()
    db.session.refresh(db_tt)
    return db_tt

@app.get('/timetable/')
async def listTT():
    tt = db.session.query(ModelTimetable).all()
    return tt

@app.get('/timetable/{id}')
async def readTT(id : int):
    tt = db.session.query(ModelTimetable).filter(ModelTimetable.id_timetable == id)
    if tt == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return tt

@app.delete('/timetable/{id}')
async def deleteTT(id : int):
    del_tt = db.session.query(ModelTimetable).filter(ModelTimetable.id_timetable == id)
    if del_tt == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_tt.delete(synchronize_session=False)
        db.session.commit()

@app.put('/timetable/{id}')
async def updateTT(id : int):
    upd_tt = db.session.query(ModelTimetable).filter(ModelTimetable.id_timetable == id)
    if upd_tt == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        upd_tt.update(synchronize_session=False)
        db.session.commit()
        return upd_tt

# To run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)