# build a schema using pydantic
from pydantic import BaseModel
from datetime import date, time

class Course(BaseModel):
    id_programme : int
    id_timetable : int
    cdate : date
    class Config:
        orm_mode = True

class Lesson(BaseModel):
    id_course : int
    ldate : date
    topic : str
    class Config:
        orm_mode = True

class LResult(BaseModel):
    id_lesson : int
    id_student : int
    id_mark : int
    class Config:
        orm_mode = True

class Mark(BaseModel):
    mark : int
    class Config:
        orm_mode = True

class Programme(BaseModel):
    level : str
    intensity : str
    book : str
    price : int
    class Config:
        orm_mode = True

class Status(BaseModel):
    status : str
    class Config:
        orm_mode = True

class StContract(BaseModel):
    id_course : int
    id_student : int
    scdate : date
    class Config:
        orm_mode = True

class Student(BaseModel):
    sname : str
    balance : int
    class Config:
        orm_mode = True

class Teacher(BaseModel):
    tname : str
    salary : int
    class Config:
        orm_mode = True

class TeaContract(BaseModel):
    id_course : int
    id_teacher : int
    tcdate : date
    class Config:
        orm_mode = True

class TeaStatus(BaseModel):
    id_status : int
    id_teacher : int
    tsdate : date
    class Config:
        orm_mode = True

class Timetable(BaseModel):
    weekday : int
    lessontime : time
    class Config:
        orm_mode = True