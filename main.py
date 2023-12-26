import uvicorn
from fastapi import FastAPI, Response, Request, status
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from sqlalchemy import desc, func
from datetime import datetime, date, time

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
intens = {"L": "Low", "M": "Medium", "I": "intense"}

async def currentCourses():
    r = []
    tts = db.session.query(ModelTimetable).all()
    for tt in tts:
        course = db.session.query(ModelCourse).filter(ModelCourse.id_timetable == tt.id_timetable).\
        order_by(desc("cdate")).first()
        if course:
            r.append(course.id_course)
    return r

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
async def main(id : int):
    cur = await currentCourses()
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
    <table>
    <tr><td>   </td><td></td></tr>
    """
    sc = db.session.query(ModelStContract).filter(ModelStContract.id_student == id).all()
    for c in sc:
        if c.id_course in cur:
            page += '<tr><td><a href="/course/' + str(c.id_course) + '">' + str(c.id_course) +\
                    '</a></td><td><button formaction="/student/remove/' + str(id) + '/' + str(c.id_course) +\
                    '" type="submit">Remove</button></td></tr>'
    page += """
    </table>
    </p>""" +\
    '<button formaction="/student/enroll/' + str(id) + \
    """ " type="submit">Enroll to course</button></p>
    </form>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/student/create/')
async def root(request : Request):
    return templates.TemplateResponse("createstudent.html", {"request": request})

@app.get('/student/edit/{id}')
async def root(request : Request, id: int):
    name = db.session.query(ModelStudent).filter(ModelStudent.id_student == id).first().sname
    return templates.TemplateResponse("editstudent.html", {"request": request, "id": id, "nm":name})

@app.get('/student/enroll/{id}')
async def root(request : Request, id: int):
    return templates.TemplateResponse("enrollstudent.html", {"request": request, "id": id})

@app.post('/student/enroll/{id}')
async def updateSt(id : int, ic : int = Form(...), scd : str = Form(None)):
    if scd:
        scd = datetime.strptime(scd, '%d.%m.%Y').date()
    else:
        scd = datetime.now().date()
    new_sc = ModelStContract(id_student = id, id_course = ic, scdate = scd)
    db.session.add(new_sc)
    db.session.commit()
    return RedirectResponse("/student/" + str(id), status.HTTP_302_FOUND) 

@app.get('/student/remove/{ids}/{idc}/')
async def root(ids: int, idc:int):
    db_sc = db.session.query(ModelStContract).filter(ModelStContract.id_student == ids,\
                                                     ModelStContract.id_course == idc)
    if db_sc == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        db_sc.delete(synchronize_session=False)
        db.session.commit()
    return RedirectResponse("/student/" + str(ids), status.HTTP_302_FOUND) 

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
    <table>
    <tr>
    <th>Name</th>
    <th>Salary</th>
    <th>Status</th>
    </tr>
    """
    for t in teacher:
        stat = db.session.query(ModelTeaStatus).filter(ModelTeaStatus.id_teacher == t.id_teacher).\
            order_by(desc("tsdate")).first().id_status
        stat = db.session.query(ModelStatus).filter(ModelStatus.id_status == stat).\
            first().status
        page += '<tr><td><a href="/teacher/' + str(t.id_teacher) + '">' +\
        t.tname +  '</a></td><td>' + str(t.salary) + '</td><td>'+ stat + '</td></tr>'
    page += """
    </table>
    </form>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/teacher/{id}')
async def readT(id : int):
    cur = await currentCourses()
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
    <h3>Teaches courses:</h3>
    <table>
    <tr><td>   </td><td></td></tr>
    """
    tc = db.session.query(ModelTeaContract).filter(ModelTeaContract.id_teacher == id).all()
    for c in tc:
        if c.id_course in cur:
            page += '<tr><td><a href="/course/' + str(c.id_course) + '">' + str(c.id_course) +\
                    '</a></td><td><button formaction="/teacher/remove/' + str(id) + '/' + str(c.id_course) +\
                    '" type="submit">Remove</button></td></tr>'
    page += """
    </table>""" +\
    '<button formaction="/teacher/assign/' + str(id) + \
    """ " type="submit">Assign to course</button></p>
   </form>
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

@app.get('/teacher/assign/{id}')
async def root(request : Request, id: int):
    name = db.session.query(ModelTeacher).filter(ModelTeacher.id_teacher == id).first().tname
    return templates.TemplateResponse("assignteacher.html", {"request": request, "id": id, "nm" : name})

@app.post('/teacher/assign/{id}')
async def updateSt(id : int, ic : int = Form(...), tcd : str = Form(None)):
    if tcd:
        tcd = datetime.strptime(tcd, '%d.%m.%Y').date()
    else:
        tcd = datetime.now().date()
    new_tc = ModelTeaContract(id_teacher = id, id_course = ic, tcdate = tcd)
    db.session.add(new_tc)
    db.session.commit()
    return RedirectResponse("/teacher/" + str(id), status.HTTP_302_FOUND) 

@app.get('/teacher/remove/{idt}/{idc}')
async def deleteT(idt : int, idc:int):
    del_tc = db.session.query(ModelTeaContract).filter(ModelTeaContract.id_teacher == idt,\
                                                       ModelTeaContract.id_course == idc)
    if del_tc == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_tc.delete(synchronize_session=False)
        db.session.commit()
        return RedirectResponse("/teacher/" + str(idt), status.HTTP_302_FOUND) 

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
        cd = datetime.strptime(cd, '%d.%m.%Y').date()
    else:
        cd = datetime.now().date()
    db_course = ModelCourse(id_programme = pr, 
                            id_timetable = tt, cdate = cd)
    db.session.add(db_course)
    db.session.commit()
    db.session.refresh(db_course)
    return RedirectResponse("/course/" + str(db_course.id_course), status.HTTP_302_FOUND)

@app.get('/course/')
async def listC():
    course = await currentCourses()
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
        c = db.session.query(ModelCourse).filter(ModelCourse.id_course == c).first()
        tt = db.session.query(ModelTimetable).filter\
            (ModelTimetable.id_timetable == c.id_timetable).first()
        page += '<tr><td><a href="/course/' + str(c.id_course) + '">' +\
            str(c.id_course) +  '</a></td><td>' + weekdays[tt.weekday] + ' ' +\
            time.strftime(tt.lessontime, '%H:%M') + '<td><a href="/programme/'+ str(c.id_programme) +\
                '">' + str(c.id_programme) + '</a></td><td>'+ date.strftime(c.cdate, '%d.%m.%Y') + '</td></tr>'
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
    time.strftime(tt.lessontime, '%H:%M') + '<td><a href="/programme/'+ str(course.id_programme) +\
        '">' + str(course.id_programme) + '</a></td><td>'+ date.strftime(course.cdate, '%d.%m.%Y') + '</td></tr>'
    page += """
    </table>"""
    teacher = db.session.query(ModelTeaContract).filter(ModelTeaContract.id_course == id).\
              order_by(desc("tcdate")).first()
    if teacher:
        teacher = db.session.query(ModelTeacher).filter(ModelTeacher.id_teacher == teacher.id_teacher).first()
        teacher = '<a href="/teacher/' + str(teacher.id_teacher) + '">' + teacher.tname + '</a>'
    else:
        teacher = "None"
    page += "<h4>Current teacher: " + teacher + "</h4>"
    scs = db.session.query(ModelStContract).filter(ModelStContract.id_course == id).all()
    page += "<h4>Students:</h4>"
    for s in scs:
        student = db.session.query(ModelStudent).filter(ModelStudent.id_student == s.id_student).first()
        page += '<p><a href="/student/' + str(student.id_student) + '">' + student.sname + '</a></p>'
    page += """
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


@app.get('/course/delete/{id}')
async def deleteC(id : int):
    del_course = db.session.query(ModelCourse).filter(ModelCourse.id_course == id)
    if del_course == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_course.delete(synchronize_session=False)
        db.session.commit()
        return RedirectResponse("/course/", status.HTTP_302_FOUND) 

@app.post('/course/{id}')
async def updateC(id : int, tt : int = Form(None), pr : int = Form(None), cd : str = Form(None)):
    if tt:
        db.session.query(ModelCourse).filter(ModelCourse.id_course == id).\
        update({"id_timetable" : tt})
    if pr:
        db.session.query(ModelCourse).filter(ModelCourse.id_course == id).\
        update({"id_programme" : pr})
    if cd:
        db.session.query(ModelCourse).filter(ModelCourse.id_course == id).\
        update({"cdate" : datetime.strptime(cd, '%d.%m.%Y').date()})
    db.session.commit()
    return RedirectResponse("/course/" + str(id), status.HTTP_302_FOUND) 
    
# mark operations
@app.post('/mark/')
def createM(mk: int = Form(...)):
    db_mark = ModelMark(mark = mk)
    db.session.add(db_mark)
    db.session.commit()
    db.session.refresh(db_mark)
    return RedirectResponse("/mark/", status.HTTP_302_FOUND)

@app.get('/mark/')
async def listM():
    mark = db.session.query(ModelMark).all()
    page = """
<html>
   <body>
    <form>
    <h2>Marks:</h2>
         <p>Click to create:
         <button formaction="/mark/create/" type="submit">Create</button></p>
    </form>
    <table>
    <tr>
    <th>Mark ID</th>
    <th>Mark Value</th>
    </tr>
    """
    for m in mark:
        page += '<tr><td><a href="/mark/' + str(m.id_mark) + '">' +\
        str(m.id_mark) + '</a></td><td>' + str(m.mark) + '</td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/mark/{id}')
async def readM(id : int):
    mark = db.session.query(ModelMark).filter(ModelMark.id_mark == id).first()
    page = """
<html>
   <body>
    <form>
    <h2>Mark:</h2>
         <p>Click to edit: """ +\
    '<button formaction="/mark/edit/' + str(id) + \
    """ " type="submit">Edit</button></p>
         <p>Click to delete: """ +\
    '<button formaction="/mark/delete/' + str(id) + \
    """ " type="submit">Delete</button></p>
    </form>
    <table>
    <tr>
    <th>Mark ID</th>
    <th>Mark Value</th>
    </tr>
    """
    page += '<tr><td>'+ str(mark.id_mark) + '</td><td>' + str(mark.mark) + '</td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/mark/create/')
async def root(request : Request):
    return templates.TemplateResponse("createmark.html", {"request": request})

@app.get('/mark/edit/{id}')
async def root(request : Request, id: int):
    return templates.TemplateResponse("editmark.html", {"request": request, "id": id})

@app.get('/mark/delete/{id}')
async def deleteM(id : int):
    del_mark = db.session.query(ModelMark).filter(ModelMark.id_mark == id)
    if del_mark == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_mark.delete(synchronize_session=False)
        db.session.commit()
        return RedirectResponse("/mark/", status.HTTP_302_FOUND) 

@app.post('/mark/{id}')
async def updateM(id : int, mk: int = Form(...)):
    db.session.query(ModelMark).filter(ModelMark.id_mark == id).\
        update({"mark": mk})
    db.session.commit()
    return RedirectResponse("/mark/", status.HTTP_302_FOUND) 
    
# status operations
@app.post('/status/')
def createStat(st:str = Form(...)):
    db_status = ModelStatus(status = st)
    db.session.add(db_status)
    db.session.commit()
    db.session.refresh(db_status)
    return RedirectResponse("/status/", status.HTTP_302_FOUND)

@app.get('/status/')
async def listStat():
    status = db.session.query(ModelStatus).all()
    page = """
<html>
   <body>
    <form>
    <h2>Marks:</h2>
         <p>Click to create:
         <button formaction="/status/create/" type="submit">Create</button></p>
    </form>
    <table>
    <tr>
    <th>Status ID</th>
    <th>Status Value</th>
    </tr>
    """
    for s in status:
        page += '<tr><td><a href="/mark/' + str(s.id_status) + '">' +\
        str(s.id_status) + '</a></td><td>' + s.status + '</td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/status/{id}')
async def readStat(id : int):
    stat = db.session.query(ModelStatus).filter(ModelStatus.id_status == id).first()
    page = """
<html>
   <body>
    <form>
    <h2>Status:</h2>
         <p>Click to edit: """ +\
    '<button formaction="/status/edit/' + str(id) + \
    """ " type="submit">Edit</button></p>
         <p>Click to delete: """ +\
    '<button formaction="/status/delete/' + str(id) + \
    """ " type="submit">Delete</button></p>
    </form>
    <table>
    <tr>
    <th>Status ID</th>
    <th>Status Value</th>
    </tr>
    """
    page += '<tr><td>'+ str(stat.id_status) + '</td><td>' + stat.status + '</td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/status/create/')
async def root(request : Request):
    return templates.TemplateResponse("createstatus.html", {"request": request})

@app.get('/status/edit/{id}')
async def root(request : Request, id: int):
    return templates.TemplateResponse("editstatus.html", {"request": request, "id": id})

@app.get('/status/delete/{id}')
async def deleteStat(id : int):
    del_status = db.session.query(ModelStatus).filter(ModelStatus.id_status == id)
    if del_status == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_status.delete(synchronize_session=False)
        db.session.commit()
        return RedirectResponse("/status/", status.HTTP_302_FOUND) 

@app.post('/status/{id}')
async def updateStat(id : int, st: str = Form(...)):
    db.session.query(ModelStatus).filter(ModelStatus.id_status == id).\
        update({"status" : st})
    db.session.commit()
    return RedirectResponse("/status/", status.HTTP_302_FOUND) 
    
# programme operations
@app.post('/programme/')
def createStat(lvl:str = Form(...), ints : str = Form(...), bk: str = Form(...),\
               pr:int = Form(...)):
    db_prog= ModelProgramme(level = lvl, intensity = ints,
                            book = bk, price = pr)
    db.session.add(db_prog)
    db.session.commit()
    db.session.refresh(db_prog)
    return RedirectResponse('/programme/' + str(db_prog.id_programme), status.HTTP_302_FOUND)

@app.get('/programme/')
async def listPr():
    prog = db.session.query(ModelProgramme).order_by("level").all()
    page = """
<html>
   <body>
    <form>
    <h2>Programmes:</h2>
         <p>Click to create:
         <button formaction="/programme/create/" type="submit">Create</button></p>
    </form>
    <table>
    <tr>
    <th>Programme Id</th>
    <th>Level</th>
    <th>Intensity</th>
    <th>Book</th>
    <th>Price</th>
    </tr>
    """
    for p in prog:
        page += '<tr><td><a href="/programme/' + str(p.id_programme) + '">' +\
            str(p.id_programme) +  '</a></td><td>' + p.level + ' ' +\
            '<td>'+ intens[p.intensity] +\
                '</td><td>' + p.book + '</td><td>'+ str(p.price) + '</td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/programme/{id}')
async def readPr(id : int):
    prog = db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id).first()
    page = """
<html>
   <body>
    <form>
    <h2>Programme:</h2>
         <p>Click to edit: """ +\
    '<button formaction="/programme/edit/' + str(id) + \
    """ " type="submit">Edit</button></p>
         <p>Click to delete: """ +\
    '<button formaction="/programme/delete/' + str(id) + \
    """ " type="submit">Delete</button></p>
    </form>
    <table>
    <tr>
    <th>Programme Id</th>
    <th>Level</th>
    <th>Intensity</th>
    <th>Book</th>
    <th>Price</th>
    </tr>
    """ +\
    '<tr><td>' + str(prog.id_programme) +  '</td><td>' + prog.level + ' ' +\
    '<td>'+ intens[prog.intensity] +'</td><td>' + prog.book + '</td><td>'+ str(prog.price) + '</td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/programme/create/')
async def root(request : Request):
    return templates.TemplateResponse("createprogramme.html", {"request": request})

@app.get('/programme/edit/{id}')
async def root(request : Request, id: int):
    return templates.TemplateResponse("editprogramme.html", {"request": request, "id": id})

@app.get('/programme/delete/{id}')
async def deletePr(id : int):
    del_prog = db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id)
    if del_prog == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_prog.delete(synchronize_session=False)
        db.session.commit()
        return RedirectResponse("/programme/", status.HTTP_302_FOUND) 

@app.post('/programme/{id}')
async def updatePr(id : int, lvl:str = Form(None), ints : str = Form(None), bk: str = Form(None),\
               pr:int = Form(None)):
    if lvl:
        db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id).\
            update({"level" : lvl})
    if ints:
        db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id).\
            update({"intensity" : ints})
    if bk:
        db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id).\
            update({"book" : bk})
    if pr:
        db.session.query(ModelProgramme).filter(ModelProgramme.id_programme == id).\
            update({"price" : pr})
    db.session.commit()
    return RedirectResponse('/programme/' + str(id), status.HTTP_302_FOUND)
    
# timetable operations
@app.post('/timetable/')
def createTT(wd:int = Form(...), lt:str = Form(...)):
    db_tt = ModelTimetable(weekday = wd, lessontime = lt)
    db.session.add(db_tt)
    db.session.commit()
    db.session.refresh(db_tt)
    return RedirectResponse("/timetable/" + str(db_tt.id_timetable), status.HTTP_302_FOUND)

@app.get('/timetable/')
async def listTT():
    tts = db.session.query(ModelTimetable).order_by("weekday").all()
    page = """
<html>
   <body>
    <form>
    <h2>Timetables:</h2>
         <p>Click to create:
         <button formaction="/timetable/create/" type="submit">Create</button></p>
    </form>
    <table>
    <tr>
    <th>Timetable Id</th>
    <th>Day</th>
    <th>Time</th>
    </tr>
    """
    for tt in tts:
        page += '<tr><td><a href="/timetable/' + str(tt.id_timetable) + '">' +\
            str(tt.id_timetable) +  '</a></td><td>' + weekdays[tt.weekday] + '</td><td>' +\
            time.strftime(tt.lessontime, '%H:%M') + '<td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/timetable/{id}')
async def readTT(id : int):
    tt = db.session.query(ModelTimetable).filter(ModelTimetable.id_timetable == id).first()
    page = """
<html>
   <body>
    <form>
    <h2>Timetable:</h2>
         <p>Click to edit: """ +\
    '<button formaction="/timetable/edit/' + str(id) + \
    """ " type="submit">Edit</button></p>
         <p>Click to delete: """ +\
    '<button formaction="/timetable/delete/' + str(id) + \
    """ " type="submit">Delete</button></p>
    </form>
    <table>
    <tr>
    <th>Timetable Id</th>
    <th>Day</th>
    <th>Time</th>
    </tr>
    """
    page += '<tr><td>' + str(id) + '</td><td>' + weekdays[tt.weekday] + '</td><td>' +\
        time.strftime(tt.lessontime, '%H:%M') + '<td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/timetable/create/')
async def root(request : Request):
    return templates.TemplateResponse("createtimetable.html", {"request": request})

@app.get('/timetable/edit/{id}')
async def root(request : Request, id: int):
    return templates.TemplateResponse("edittimetable.html", {"request": request, "id": id})

@app.get('/timetable/delete/{id}')
async def deleteTT(id : int):
    del_tt = db.session.query(ModelTimetable).filter(ModelTimetable.id_timetable == id)
    if del_tt == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_tt.delete(synchronize_session=False)
        db.session.commit()
        return RedirectResponse("/timetable/", status.HTTP_302_FOUND) 

@app.post('/timetable/{id}')
async def updateTT(id : int, wd:int = Form(None), lt: str = Form(None)):
    cur_tt = db.session.query(ModelTimetable).filter(ModelTimetable.id_timetable == id).first()
    if lt:
        lt = datetime.strptime(lt, '%H:%M').time()
    else:
        lt = cur_tt.lessontime
    if wd == None:
        wd = cur_tt.weekday
    db.session.query(ModelTimetable).filter(ModelTimetable.id_timetable == id).\
    update({"lessontime" : lt, "weekday": wd})
    db.session.commit()
    return RedirectResponse("/timetable/" + str(id), status.HTTP_302_FOUND)
    
# lesson operations
@app.post('/lesson/')
def createLes(ic:int = Form(...), ld:str = Form(...), t:str = Form(None)):
    db_les = ModelLesson(id_course = ic, ldate = datetime.strptime(ld,'%d.%m.%Y').date(), 
                         topic = t)
    db.session.add(db_les)
    db.session.commit()
    db.session.refresh(db_les)
    return RedirectResponse("/lesson/" + str(db_les.id_lesson), status.HTTP_302_FOUND)

@app.get('/lesson/')
async def listLes():
    les = db.session.query(ModelLesson).order_by("ldate").all()
    page = """
<html>
   <body>
    <form>
    <h2>Lessons:</h2>
         <p>Click to create:
         <button formaction="/lesson/create/" type="submit">Create</button></p>
    </form>
    <table>
    <tr>
    <th>Lesson ID</th>
    <th>Course ID</th>
    <th>Date</th>
    <th>Topic</th>
    </tr>
    """
    for l in les:
        if l.topic:
            t = l.topic
        else:
            t = " - "
        page += '<tr><td><a href="/lesson/' + str(l.id_lesson) + '">' + str(l.id_lesson)
        page += '</a></td><td><a href="/course/' + str(l.id_course) + '">' + str(l.id_course)
        page += '</a></td><td>' + date.strftime(l.ldate, "%d.%m.%Y") + '</td><td>' + t + '</td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/lesson/{id}')
async def readLes(id : int):
    les = db.session.query(ModelLesson).filter(ModelLesson.id_lesson == id).first()
    page = """
<html>
   <body>
    <form>
    <h2>Lesson:</h2>
          <p>Click to edit: """ +\
    '<button formaction="/lesson/edit/' + str(id) + \
    """ " type="submit">Edit</button></p>
         <p>Click to delete: """ +\
    '<button formaction="/lesson/delete/' + str(id) + \
    """ " type="submit">Delete</button></p>
    </form>
    <table>
    <tr>
    <th>Lesson ID</th>
    <th>Course ID</th>
    <th>Date</th>
    <th>Topic</th>
    </tr>
    """
    if les.topic:
        t = les.topic
    else:
        t = " - "
    page += '<tr><td>' + str(id)
    page += '</td><td><a href="/course/' + str(les.id_course) + '">' + str(les.id_course)
    page += '</a></td><td>' + date.strftime(les.ldate, "%d.%m.%Y") + '</td><td>' + t + '</td></tr>'
    page += """
</table>
<h3>Attendance:</h3>
<table>
"""
    students = db.session.query(ModelStContract)\
        .filter(ModelStContract.id_course == les.id_course).all()
    for st in students:
        name = db.session.query(ModelStudent).filter(ModelStudent.id_student == st.id_student).first().sname
        res = db.session.query(ModelLResult).filter(ModelLResult.id_student == st.id_student,\
                                                    ModelLResult.id_lesson == id).first()
        if res == None:
            r = " - "
        else:
            if res.id_mark == None:
                r = " + "
            else:
                r = str(db.session.query(ModelMark).filter(ModelMark.id_mark == res.id_mark).first().mark)
        page += '<tr><td>' + name + '</td><td><a href="/lesson/' + str(id) + '/' \
                + str(st.id_student) + '">' + r + '</a></td></tr>'
    page += """
    </table>
   </body>
</html>
"""
    return HTMLResponse(page)

@app.get('/lesson/{il}/{ist}')
async def res(request:Request, il:int, ist:int):
    sn = db.session.query(ModelStudent).filter(ModelStudent.id_student == ist).first().sname
    ld = db.session.query(ModelLesson).filter(ModelLesson.id_lesson == il).first().ldate
    ld = date.strftime(ld, '%d.%m.%Y')
    return templates.TemplateResponse("editresult.html", {"request":request, "il":il,
                                                        "ist":ist, "nm":sn, "ld":ld})

@app.post('/lesson/{il}/{ist}')
async def res(il:int, ist:int, mk:str = Form(...)):
    res = db.session.query(ModelLResult).filter(ModelLResult.id_student == ist, \
                                                ModelLResult.id_lesson == il)
    if res.first() == None:
        if mk != '-':
            if mk =='+':
                db_lr = ModelLResult(id_student = ist, id_lesson = il)
                db.session.add(db_lr)
                db.session.commit()
            else:
                db_lr = ModelLResult(id_student = ist, id_lesson = il, id_mark = int(mk))
                db.session.add(db_lr)
                db.session.commit()
    else:
        if mk == '-':
            res.delete(synchronize_session=False)
            db.session.commit()
        elif mk == '+':
            res.update({"id_mark":None})
            db.session.commit()
        else:
            res.update({"id_mark":int(mk)})
            db.session.commit()
    return RedirectResponse("/lesson/" + str(il), status.HTTP_302_FOUND)



@app.get('/lesson/create/')
async def root(request : Request):
    return templates.TemplateResponse("createlesson.html", {"request": request})

@app.get('/lesson/edit/{id}')
async def root(request : Request, id: int):
    return templates.TemplateResponse("editlesson.html", {"request": request, "id": id})

@app.get('/lesson/delete/{id}')
async def deleteLes(id : int):
    del_les = db.session.query(ModelLesson).filter(ModelLesson.id_lesson == id)
    if del_les == None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        del_les.delete(synchronize_session=False)
        db.session.commit()
        return RedirectResponse("/lesson/", status.HTTP_302_FOUND)

@app.post('/lesson/{id}')
async def updateLes(id : int, ic:int = Form(None), ld:str = Form(None), t:str = Form(None)):
    if ic:
        db.session.query(ModelLesson).filter(ModelLesson.id_lesson == id).\
        update({"id_course" : ic})
    if ld:
        ld = datetime.strptime(ld, '%d.%m.%Y').date()
        db.session.query(ModelLesson).filter(ModelLesson.id_lesson == id).\
        update({"ldate" : ld})
    if t:
        db.session.query(ModelLesson).filter(ModelLesson.id_lesson == id).\
        update({"topic" : t})
    db.session.commit()
    return RedirectResponse("/lesson/" + str(id), status.HTTP_302_FOUND)
    
# To run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)