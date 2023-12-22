import uvicorn
from fastapi import FastAPI, Response, Request, status
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from sqlalchemy import desc, func

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

templates = Jinja2Templates(directory="template")

app = FastAPI()

# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])

weekdays = {1:"Mon", 2:"Tue", 3:"Wed", 4:"Thu", 5:"Fri", 6:"Sat", 7:"Sun"}


@app.get('/')
async def root(request : Request):
    return templates.TemplateResponse("start.html", {"request": request})

@app.get('/admin')
async def root(request : Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get('/user')
async def root(request : Request):
    return templates.TemplateResponse("user.html", {"request": request})

@app.post("/table/")
async def submit(tables : str = Form(...)):
    return RedirectResponse("/" + tables, status.HTTP_302_FOUND)

# student operations

@app.post('/student/')
def createSt(nm: str = Form(...), bl:int = Form(None)):
    if not bl:
        bl = 0
    db_student = ModelStudent(sname = nm, balance = bl)
    db.session.add(db_student)
    db.session.commit()
    db.session.refresh(db_student)
    return RedirectResponse("/student/" + str(db_student.id_student), status.HTTP_302_FOUND)

@app.get("/student/")
def main():
    student = db.session.query(ModelStudent).all()
    page = """
<html>
   <body>
    <form>
    <h2>Students:</h2>
         <p>Click to create:
         <button formaction="/student/create/" type="submit">Create</button></p>
    </form>
    <table>
    <tr>
    <th>Name</th>
    <th>Balance</th>
    </tr>
    """
    for s in student:
        page += '<tr><td><a href="/student/' + str(s.id_student) + '">' +\
        s.sname +  '</a></td><td>' + str(s.balance) + '</td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)
    
@app.get('/student/{id}')
def main(id : int):
    student = db.session.query(ModelStudent).filter(ModelStudent.id_student == id).first()
    page = """
<html>
   <body>
    <form>
    <h2>Student:</h2>
         <p>Click to edit: """ +\
    '<button formaction="/student/edit/' + str(id) + \
    """ " type="submit">Edit</button></p>
         <p>Click to delete: """ +\
    '<button formaction="/student/delete/' + str(id) + \
    """ " type="submit">Delete</button></p>
    </form>
    <table>
    <tr>
    <th>Name</th>
    <th>Balance</th>
    </tr>
    """
    page += '<tr><td>'+ student.sname + '</td><td>' + str(student.balance) + '</td></tr>'
    page += """
    </table>
    <h3>Attends courses:</h3>
    <p>"""
    sc = db.session.query(ModelStContract).filter(ModelStContract.id_student == id)
    for c in sc:
        page += str(c.id_course) + ' '
    page += """
    </p>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/student/create/')
async def root(request : Request):
    return templates.TemplateResponse("createstudent.html", {"request": request})

@app.get('/student/edit/{id}')
async def root(request : Request, id: int):
    return templates.TemplateResponse("editstudent.html", {"request": request, "id": id})

@app.get('/student/delete/{id}')
async def deleteSt(id : int):
    del_student = db.session.query(ModelStudent).filter(ModelStudent.id_student == id)
    if del_student == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_student.delete(synchronize_session=False)
        db.session.commit()
        return RedirectResponse("/student/", status.HTTP_302_FOUND) 

@app.post('/student/{id}')
async def updateSt(id : int, nm : str = Form(None), bl : int = Form(None)):
    if nm:
        db.session.query(ModelStudent).filter(ModelStudent.id_student == id).\
            update({"sname" : nm}, synchronize_session=False)
    if bl:
        db.session.query(ModelStudent).filter(ModelStudent.id_student == id).\
            update({"balance" : bl}, synchronize_session=False)
    db.session.commit()
    return RedirectResponse("/student/" + str(id), status.HTTP_302_FOUND) 

 # teacher operations 
@app.post('/teacher/')
def createT(nm: str = Form(...), sl:int = Form(None)):
    if not sl:
        sl = 0
    db_teacher = ModelTeacher(tname= nm, salary = sl)
    db.session.add(db_teacher)
    db.session.commit()
    db.session.refresh(db_teacher)
    return RedirectResponse("/teacher/" + str(db_teacher.id_teacher), status.HTTP_302_FOUND)

@app.get('/teacher/')
async def listT():
    teacher = db.session.query(ModelTeacher).all()
    page = """
<html>
   <body>
    <form>
    <h2>Teachers:</h2>
         <p>Click to create: 
         <button formaction="/teacher/create/" type="submit">Create</button></p>
    </form>
    <table>
    <tr>
    <th>Name</th>
    <th>Salary</th>
    <th>Status</th>
    </tr>
    """
    for t in teacher:
        stat = db.session.query(ModelTeaStatus).filter(ModelTeaStatus.id_teacher == id).\
            order_by(desc('tsdate')).first().id_status
        stat = db.session.query(ModelStatus).filter(ModelStatus.id_status == stat).\
            first().status
        page += '<tr><td><a href="/teacher/' + str(t.id_teacher) + '">' +\
        t.tname +  '</a></td><td>' + str(t.salary) + '</td><td>'+ stat + '</td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/teacher/{id}')
async def readT(id : int):
    teacher = db.session.query(ModelTeacher).filter(ModelTeacher.id_teacher == id).first()
    stat = db.session.query(ModelTeaStatus).filter(ModelTeaStatus.id_teacher == id).\
        order_by(desc('tsdate')).first().id_status
    stat = db.session.query(ModelStatus).filter(ModelStatus.id_status == stat).\
        first().status
    page = """
<html>
   <body>
    <form>
    <h2>Teacher:</h2>
         <p>Click to edit: """ +\
    '<button formaction="/teacher/edit/' + str(id) + \
    """ " type="submit">Edit</button></p>
         <p>Click to delete: """ +\
    '<button formaction="/teacher/delete/' + str(id) + \
    """ " type="submit">Delete</button></p>
    </form>
    <table>
    <tr>
    <th>Name</th>
    <th>Salary</th>
    <th>Status</th>
    </tr>
    """
    page += '<tr><td>'+ teacher.tname + '</td><td>' + str(teacher.salary) + \
        '</td><td>' + stat + '</td></tr>'
    page += """
    </table>
    <h3>Attends courses:</h3>
    <p>"""
    # sc = db.session.query(ModelStContract).filter(ModelStContract.id_student == id)
    # for c in sc:
    #     page += str(c.id_course) + ' '
    page += """
    </p>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/teacher/create/')
async def root(request : Request):
    return templates.TemplateResponse("createteacher.html", {"request": request})

@app.get('/teacher/edit/{id}')
async def root(request : Request, id: int):
    return templates.TemplateResponse("editteacher.html", {"request": request, "id": id})

@app.get('/teacher/delete/{id}')
async def deleteT(id : int):
    del_teacher = db.session.query(ModelTeacher).filter(ModelTeacher.id_teacher == id)
    if del_teacher == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_teacher.delete(synchronize_session=False)
        db.session.commit()
        return RedirectResponse("/teacher/", status.HTTP_302_FOUND) 

@app.post('/teacher/{id}')
async def updateT(id : int, nm : str = Form(None), sl : int = Form(None)):
    if nm:
        db.session.query(ModelTeacher).filter(ModelTeacher.id_teacher == id).\
            update({"tname" : nm})
    if sl:
        db.session.query(ModelTeacher).filter(ModelTeacher.id_teacher == id).\
            update({"salary" : sl})
    db.session.commit()
    return RedirectResponse("/teacher/" + str(id), status.HTTP_302_FOUND) 
    
# course operations
@app.post('/course/')
def createC(pr : int = Form(...), tt : int = Form(...), cd : str = Form(None)):
    if cd:
        cd = func.to_date(cd)
    else:
        cd = func.to_date(func.now())
    db_course = ModelCourse(id_programme = pr, 
                            id_timetable = tt, cdate = cd)
    db.session.add(db_course)
    db.session.commit()
    db.session.refresh(db_course)
    return RedirectResponse("/course/" + str(db_course.id_course), status.HTTP_302_FOUND)

@app.get('/course/')
async def listC():
    course = db.session.query(ModelCourse).all()
    page = """
<html>
   <body>
    <form>
    <h2>Current courses:</h2>
         <p>Click to create:
         <button formaction="/course/create/" type="submit">Create</button></p>
    </form>
    <table>
    <tr>
    <th>Course Id</th>
    <th>Time</th>
    <th>Programme</th>
    <th>Start</th>
    </tr>
    """
    for c in course:
        tt = db.session.query(ModelTimetable).filter\
            (ModelTimetable.id_timetable == c.id_timetable).first()
        page += '<tr><td><a href="/course/' + str(c.id_course) + '">' +\
            str(c.id_course) +  '</a></td><td>' + weekdays[tt.weekday] + ' ' +\
            str(tt.lessontime) + '<td><a href="/programme/'+ str(c.id_programme) +\
                '">' + str(c.id_programme) + '</a></td><td>'+ str(c.cdate) + '</td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/course/{id}')
async def readC(id : int):
    course = db.session.query(ModelCourse).filter(ModelCourse.id_course == id).first()
    tt = db.session.query(ModelTimetable).filter\
        (ModelTimetable.id_timetable == course.id_timetable).first()
    page = """
<html>
   <body>
    <form>
    <h2>Course:</h2>
         <p>Click to edit: """ +\
    '<button formaction="/course/edit/' + str(id) + \
    """ " type="submit">Edit</button></p>
         <p>Click to delete: """ +\
    '<button formaction="/course/delete/' + str(id) + \
    """ " type="submit">Delete</button></p>
    </form>
    <table>
    <tr>
    <th>Course Id</th>
    <th>Time</th>
    <th>Programme</th>
    <th>Start</th>
    </tr>
    """ +\
    '<tr><td><a href="/course/' + str(course.id_course) + '">' +\
    str(course.id_course) +  '</a></td><td>' + weekdays[tt.weekday] + ' ' +\
    str(tt.lessontime) + '<td><a href="/programme/'+ str(course.id_programme) +\
        '">' + str(course.id_programme) + '</a></td><td>'+ str(course.cdate) + '</td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/course/create/')
async def root(request : Request):
    return templates.TemplateResponse("createcourse.html", {"request": request})

@app.get('/course/edit/{id}')
async def root(request : Request, id: int):
    return templates.TemplateResponse("editcourse.html", {"request": request, "id": id})


@app.delete('/course/{id}')
async def deleteC(id : int):
    del_course = db.session.query(ModelCourse).filter(ModelCourse.id_course == id)
    if del_course == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_course.delete(synchronize_session=False)
        db.session.commit()

@app.put('/course/{id}', response_model=SchemaCourse)
async def updateC(id : int, c : SchemaCourse):
    db.session.query(ModelCourse).filter(ModelCourse.id_course == id).\
        update({"id_programme" : c.id_programme,\
                "id_timetable" : c.id_timetable, "cdate" : c.cdate})
    db.session.commit()
    return db.session.query(ModelCourse).filter(ModelCourse.id_course == id).first()
    
# mark operations
@app.post('/mark/', response_model=SchemaMark)
def createM(mark: SchemaMark):
    db_mark = ModelMark(mark = mark.mark)
    db.session.add(db_mark)
    db.session.commit()
    db.session.refresh(db_mark)
    return db_mark

@app.get('/mark/')
async def listM():
    mark = db.session.query(ModelMark).all()
    return mark

@app.get('/mark/{id}', response_model=SchemaMark)
async def readM(id : int):
    mark = db.session.query(ModelMark).filter(ModelMark.id_mark == id)
    if mark == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return mark.first()

@app.delete('/mark/{id}')
async def deleteM(id : int):
    del_mark = db.session.query(ModelMark).filter(ModelMark.id_mark == id)
    if del_mark == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_mark.delete(synchronize_session=False)
        db.session.commit()

@app.put('/mark/{id}' , response_model=SchemaMark)
async def updateM(id : int, nmark: SchemaMark):
    db.session.query(ModelMark).filter(ModelMark.id_mark == id).\
        update({"mark": nmark.mark})
    db.session.commit()
    return db.session.query(ModelMark).filter(ModelMark.id_mark == id).first()
    
# status operations
@app.post('/status/', response_model=SchemaStatus)
def createStat(status: SchemaStatus):
    db_status = ModelStatus(status = status.status)
    db.session.add(db_status)
    db.session.commit()
    db.session.refresh(db_status)
    return db_status

@app.get('/status/')
async def listStat():
    status = db.session.query(ModelStatus).all()
    return status

@app.get('/status/{id}', response_model=SchemaStatus)
async def readStat(id : int):
    stat = db.session.query(ModelStatus).filter(ModelStatus.id_status == id)
    if stat == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return stat.first()

@app.delete('/status/{id}')
async def deleteStat(id : int):
    del_status = db.session.query(ModelStatus).filter(ModelStatus.id_status == id)
    if del_status == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_status.delete(synchronize_session=False)
        db.session.commit()

@app.put('/status/{id}', response_model=SchemaStatus)
async def updateStat(id : int, stat :SchemaStatus):
    db.session.query(ModelStatus).filter(ModelStatus.id_status == id).\
        update({"status" : stat.status})
    db.session.commit()
    return db.session.query(ModelStatus).filter(ModelStatus.id_status == id).first()
    
# programme operations
@app.post('/programme/', response_model=SchemaProgramme)
def createStat(prog: SchemaProgramme):
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

@app.get('/programme/{id}', response_model=SchemaProgramme)
async def readPr(id : int):
    prog = db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id)
    if prog == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return prog.first()

@app.delete('/programme/{id}')
async def deletePr(id : int):
    del_prog = db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id)
    if del_prog == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_prog.delete(synchronize_session=False)
        db.session.commit()

@app.put('/programme/{id}', response_model=SchemaProgramme)
async def updatePr(id : int, prog : SchemaProgramme):
    db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id).\
        update({"level" : prog.level, "intensity" : prog.intensity,
                            "book" : prog.book, "price" : prog.price})
    db.session.commit()
    return db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id).first()
    
# timetable operations
@app.post('/timetable/', response_model=SchemaTimetable)
def createTT(tt: SchemaTimetable):
    db_tt = ModelTimetable(lessontime = tt.lessontime, weekday = tt.weekday)
    db.session.add(db_tt)
    db.session.commit()
    db.session.refresh(db_tt)
    return db_tt

@app.get('/timetable/')
async def listTT():
    tt = db.session.query(ModelTimetable).all()
    return tt

@app.get('/timetable/{id}', response_model=SchemaTimetable)
async def readTT(id : int):
    tt = db.session.query(ModelTimetable).filter(ModelTimetable.id_timetable == id)
    if tt == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return tt.first()

@app.delete('/timetable/{id}')
async def deleteTT(id : int):
    del_tt = db.session.query(ModelTimetable).filter(ModelTimetable.id_timetable == id)
    if del_tt == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_tt.delete(synchronize_session=False)
        db.session.commit()

@app.put('/timetable/{id}', response_model=SchemaTimetable)
async def updateTT(id : int, tt : SchemaTimetable):
    db.session.query(ModelTimetable).filter(ModelTimetable.id_timetable == id).\
        update({"lessontime" : tt.lessontime, "weekday" : tt.weekday})
    db.session.commit()
    return db.session.query(ModelTimetable).filter(ModelTimetable.id_timetable == id).first()
    
# lesson operations
@app.post('/lesson/', response_model=SchemaLesson)
def createLes(les: SchemaLesson):
    db_les = ModelLesson(id_course = les.id_course, ldate = les.ldate, 
                         topic = les.topic)
    db.session.add(db_les)
    db.session.commit()
    db.session.refresh(db_les)
    return db_les

@app.get('/lesson/')
async def listLes():
    les = db.session.query(ModelLesson).all()
    return les

@app.get('/lesson/{id}', response_model=SchemaLesson)
async def readLes(id : int):
    les = db.session.query(ModelLesson).filter(ModelLesson.id_lesson == id)
    if les == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return les.first()

@app.delete('/lesson/{id}')
async def deleteLes(id : int):
    del_les = db.session.query(ModelLesson).filter(ModelLesson.id_lesson == id)
    if del_les == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_les.delete(synchronize_session=False)
        db.session.commit()

@app.put('/lesson/{id}', response_model=SchemaLesson)
async def updateLes(id : int, les : SchemaLesson):
    db.session.query(ModelLesson).filter(ModelLesson.id_lesson == id).\
        update({"id_course" : les.id_course, "ldate" : les.ldate, "topic" : les.topic})
    db.session.commit()
    return db.session.query(ModelLesson).filter(ModelLesson.id_lesson == id).first()
    
# lresult operations
@app.post('/lresult/', response_model=SchemaLResult)
def createLR(lr: SchemaLResult):
    db_lr = ModelLResult(id_student = lr.id_student, id_lesson = lr.id_lesson,
                         id_mark = lr.id_mark)
    db.session.add(db_lr)
    db.session.commit()
    db.session.refresh(db_lr)
    return db_lr

@app.get('/lresult/')
async def listLR():
    lr = db.session.query(ModelLResult).all()
    return lr

@app.get('/lresult/{idl}/{ids}', response_model=SchemaLResult)
async def readLR(idl : int, ids : int):
    lr = db.session.query(ModelLResult).filter(ModelLResult.id_lesson == idl and
                                               ModelLResult.id_student == ids)
    if lr == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return lr.first()

@app.delete('/lresult/{idl}/{ids}')
async def deleteLR(idl : int, ids : int):
    del_lr = db.session.query(ModelLResult).filter(ModelLResult.id_lesson == idl and
                                                   ModelLResult.id_student == ids)
    if del_lr == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_lr.delete(synchronize_session=False)
        db.session.commit()

@app.put('/lresult/{idl}/{ids}', response_model=SchemaLResult)
async def updateLR(idl : int, ids : int, lr : SchemaLResult):
    db.session.query(ModelLResult).filter(ModelLResult.id_lesson == idl and
        ModelLResult.id_student == ids).update({"id_student" : lr.id_student, 
            "id_lesson" : lr.id_lesson, "id_mark" : lr.id_mark})
    db.session.commit()
    return db.session.query(ModelLResult).filter(ModelLResult.id_lesson == idl and
        ModelLResult.id_student == ids).first()
    
# stcontract operations
@app.post('/stcontract/', response_model=SchemaStContract)
def createSC(sc: SchemaStContract):
    db_sc = ModelStContract(id_student = sc.id_student, id_course = sc.id_course,
                         scdate = sc.scdate)
    db.session.add(db_sc)
    db.session.commit()
    db.session.refresh(db_sc)
    return db_sc

@app.get('/stcontract/')
async def listSC():
    sc = db.session.query(ModelStContract).all()
    return sc

@app.get('/stcontract/{idc}/{ids}', response_model=SchemaStContract)
async def readSC(idc : int, ids : int):
    sc = db.session.query(ModelStContract).filter(ModelStContract.id_course == idc and
                                               ModelStContract.id_student == ids)
    if sc == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return sc.first()

@app.delete('/stcontract/{idc}/{ids}')
async def deleteSC(idc : int, ids : int):
    del_sc = db.session.query(ModelStContract).filter(ModelStContract.id_course == idc and
                                                   ModelStContract.id_student == ids)
    if del_sc == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_sc.delete(synchronize_session=False)
        db.session.commit()

@app.put('/stcontract/{idc}/{ids}', response_model=SchemaStContract)
async def updateSC(idc : int, ids : int, sc : SchemaStContract):
    db.session.query(ModelStContract).filter(ModelStContract.id_course == idc and
        ModelStContract.id_student == ids).update({"id_student" : sc.id_student, 
            "id_course" : sc.id_course, "scdate" : sc.scdate})
    db.session.commit()
    return db.session.query(ModelStContract).filter(ModelStContract.id_course == idc and
                            ModelStContract.id_student == ids).first()
    
# teastatus operations
@app.post('/teastatus/', response_model=SchemaTeaStatus)
def createTS(ts: SchemaTeaStatus):
    db_ts = ModelTeaStatus(id_teacher = ts.id_teacher, id_status = ts.id_status,
                           tsdate = ts.tsdate)
    db.session.add(db_ts)
    db.session.commit()
    db.session.refresh(db_ts)
    return db_ts

@app.get('/teastatus/')
async def listTS():
    ts = db.session.query(ModelTeaStatus).all()
    return ts

@app.get('/teastatus/{id}')
async def readTS(id : int):
    ts = db.session.query(ModelTeaStatus).filter(ModelTeaStatus.id_tst == id)
    ts.first()
    if ts == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return ts.first()

@app.delete('/teastatus/{id}', response_model=SchemaTeaStatus)
async def deleteTS(id : int):
    del_ts = db.session.query(ModelTeaStatus).filter(ModelTeaStatus.id_tst == id)
    if del_ts == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_ts.delete(synchronize_session=False)
        db.session.commit()

@app.put('/teastatus/{id}')
async def updateTS(id : int, ts : SchemaTeaStatus):
    db.session.query(ModelTeaStatus).filter(ModelTeaStatus.id_tst == id).\
        update({"id_teacher" : ts.id_teacher, "id_status" : ts.id_status,"tsdate" : ts.tsdate})
    db.session.commit()
    return db.session.query(ModelTeaStatus).filter(ModelTeaStatus.id_tst == id).first()
    
# teacontract operations
@app.post('/teacontract/', response_model=SchemaTeaContract)
def createTC(tc: SchemaTeaContract):
    db_tc = ModelTeaContract(id_teacher = tc.id_teacher, id_course = tc.id_course,
                         tcdate = tc.tcdate)
    db.session.add(db_tc)
    db.session.commit()
    db.session.refresh(db_tc)
    return db_tc

@app.get('/teacontract/')
async def listTC():
    tc = db.session.query(ModelTeaContract).all()
    return tc

@app.get('/teacontract/{idc}/{idt}', response_model=SchemaTeaContract)
async def readTC(idc : int, idt : int):
    tc = db.session.query(ModelTeaContract).filter(ModelTeaContract.id_course == idc and
                                               ModelTeaContract.id_teacher == idt)
    if tc == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return tc.first()

@app.delete('/teacontract/{idc}/{idt}')
async def deleteTC(idc : int, idt : int):
    del_tc = db.session.query(ModelTeaContract).filter(ModelTeaContract.id_course == idc and
                                                   ModelTeaContract.id_teacher == idt)
    if del_tc == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_tc.delete(synchronize_session=False)
        db.session.commit()

@app.put('/teacontract/{idc}/{idt}', response_model=SchemaTeaContract)
async def updateTC(idc : int, idt : int, tc : SchemaTeaContract):
    db.session.query(ModelTeaContract).filter(ModelTeaContract.id_course == idc and
        ModelTeaContract.id_teacher == idt).update({"id_teacher" : tc.id_teacher, 
            "id_course" : tc.id_course, "tcdate" : tc.tcdate})
    db.session.commit()
    return db.session.query(ModelTeaContract).filter(ModelTeaContract.id_course == idc and
                ModelTeaContract.id_teacher == idt).first()
    
# To run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)