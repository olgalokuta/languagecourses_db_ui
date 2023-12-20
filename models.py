from sqlalchemy import Column, Date, Time, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base  = declarative_base()

class Course(Base):
    __tablename__ = 'course'
    id_course = Column(Integer, primary_key=True)
    id_programme = Column(Integer, ForeignKey('programme.id_programme'))
    id_timetable = Column(Integer, ForeignKey('timetable.id_timetable'))
    cdate = Column(Date)
    programme = relationship('Programme')
    timetable = relationship('Timetable')

class Lesson(Base):
    __tablename__ = 'lesson'
    id_lesson = Column(Integer, primary_key=True)
    id_course = Column(Integer, ForeignKey('course.id_course'))
    ldate = Column(Date)
    topic = Column(String)
    course = relationship('Course')

class LResult(Base):
    __tablename__ = 'lresult'
    id_lesson = Column(Integer, ForeignKey('lesson.id_lesson'), primary_key=True)
    id_student = Column(Integer, ForeignKey('student.id_student'), primary_key=True)
    id_mark = Column(Integer, ForeignKey('mark.id_mark'))
    lesson = relationship('Lesson')
    student = relationship('Student')
    mark = relationship('Mark')

class Mark(Base):
    __tablename__ = 'mark'
    id_mark = Column(Integer, primary_key=True)
    mark = Column(Integer)

class Programme(Base):
    __tablename__ = 'programme'
    id_programme = Column(Integer, primary_key=True)
    level = Column(String)
    intensity = Column(String)
    book = Column(String)
    price = Column(Integer)

class Status(Base):
    __tablename__ = 'status'
    id_status = Column(Integer, primary_key=True)
    status = Column(String)

class StContract(Base):
    __tablename__ = 'stcontract'
    id_course = Column(Integer, ForeignKey('course.id_course'), primary_key=True)
    id_student = Column(Integer, ForeignKey('student.id_student'), primary_key=True)
    scdate = Column(Date)
    student = relationship('Student')
    course = relationship('Course')

class Student(Base):
    __tablename__ = 'student'
    id_student = Column(Integer, primary_key = True)
    sname = Column(String)
    balance = Column(Integer)

class Teacher(Base):
    __tablename__ = 'teacher'
    id_teacher = Column(Integer, primary_key = True)
    tname = Column(String)
    salary = Column(Integer)

class TeaContract(Base):
    __tablename__ = 'teacontract'
    id_course = Column(Integer, ForeignKey('course.id_course'), primary_key=True)
    id_teacher = Column(Integer, ForeignKey('teacher.id_teacher'), primary_key=True)
    tcdate = Column(Date)
    teacher = relationship('Teacher')
    course = relationship('Course')

class TeaStatus(Base):
    __tablename__ = 'teastatus'
    id_tst = Column(Integer, primary_key = True)
    id_status = Column(Integer, ForeignKey('status.id_status'))
    id_teacher = Column(Integer, ForeignKey('teacher.id_teacher'))
    tsdate = Column(Date)
    teacher = relationship('Teacher')
    status = relationship('Status')

class Timetable(Base):
    __tablename__ = 'timetable'
    id_timetable = Column(Integer, primary_key = True)
    weekday = Column(Integer)
    lessontime = Column(Time)
