"""New Migration

Revision ID: a06e18b76490
Revises: 
Create Date: 2023-12-20 23:16:48.437985

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a06e18b76490'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('course', 'id_programme',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('course', 'id_timetable',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('course', 'cdate',
               existing_type=sa.DATE(),
               nullable=True)
    op.alter_column('lesson', 'id_course',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('lesson', 'ldate',
               existing_type=sa.DATE(),
               nullable=True)
    op.drop_index('lres_stu_les', table_name='lresult')
    op.alter_column('mark', 'mark',
               existing_type=sa.SMALLINT(),
               type_=sa.Integer(),
               nullable=True)
    op.drop_constraint('mark_mark_key', 'mark', type_='unique')
    op.alter_column('programme', 'level',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               nullable=True)
    op.alter_column('programme', 'intensity',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               nullable=True)
    op.alter_column('programme', 'book',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('programme', 'price',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_index('programme_level_ind', table_name='programme')
    op.alter_column('status', 'status',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               nullable=True)
    op.drop_constraint('status_status_key', 'status', type_='unique')
    op.alter_column('stcontract', 'scdate',
               existing_type=sa.DATE(),
               nullable=True)
    op.alter_column('student', 'sname',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               nullable=True)
    op.alter_column('student', 'balance',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_index('student_ind', table_name='student')
    op.drop_constraint('student_sname_key', 'student', type_='unique')
    op.alter_column('teacher', 'tname',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               nullable=True)
    op.alter_column('teacher', 'salary',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint('teacher_tname_key', 'teacher', type_='unique')
    op.alter_column('teacontract', 'tcdate',
               existing_type=sa.DATE(),
               nullable=True)
    op.alter_column('teastatus', 'id_status',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('teastatus', 'id_teacher',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('teastatus', 'tsdate',
               existing_type=sa.DATE(),
               nullable=True)
    op.drop_index('workingteacher', table_name='teastatus', postgresql_where='(id_status = 1)', postgresql_include=['tsdate'])
    op.alter_column('timetable', 'weekday',
               existing_type=sa.SMALLINT(),
               type_=sa.Integer(),
               nullable=True)
    op.alter_column('timetable', 'lessontime',
               existing_type=postgresql.TIME(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('timetable', 'lessontime',
               existing_type=postgresql.TIME(),
               nullable=False)
    op.alter_column('timetable', 'weekday',
               existing_type=sa.Integer(),
               type_=sa.SMALLINT(),
               nullable=False)
    op.create_index('workingteacher', 'teastatus', ['id_teacher'], unique=False, postgresql_where='(id_status = 1)', postgresql_include=['tsdate'])
    op.alter_column('teastatus', 'tsdate',
               existing_type=sa.DATE(),
               nullable=False)
    op.alter_column('teastatus', 'id_teacher',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('teastatus', 'id_status',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('teacontract', 'tcdate',
               existing_type=sa.DATE(),
               nullable=False)
    op.create_unique_constraint('teacher_tname_key', 'teacher', ['tname'])
    op.alter_column('teacher', 'salary',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('teacher', 'tname',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               nullable=False)
    op.create_unique_constraint('student_sname_key', 'student', ['sname'])
    op.create_index('student_ind', 'student', ['id_student'], unique=False)
    op.alter_column('student', 'balance',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('student', 'sname',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               nullable=False)
    op.alter_column('stcontract', 'scdate',
               existing_type=sa.DATE(),
               nullable=False)
    op.create_unique_constraint('status_status_key', 'status', ['status'])
    op.alter_column('status', 'status',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               nullable=False)
    op.create_index('programme_level_ind', 'programme', ['id_programme', 'level'], unique=False)
    op.alter_column('programme', 'price',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('programme', 'book',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('programme', 'intensity',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               nullable=False)
    op.alter_column('programme', 'level',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               nullable=False)
    op.create_unique_constraint('mark_mark_key', 'mark', ['mark'])
    op.alter_column('mark', 'mark',
               existing_type=sa.Integer(),
               type_=sa.SMALLINT(),
               nullable=False)
    op.create_index('lres_stu_les', 'lresult', ['id_student', 'id_lesson'], unique=True)
    op.alter_column('lesson', 'ldate',
               existing_type=sa.DATE(),
               nullable=False)
    op.alter_column('lesson', 'id_course',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('course', 'cdate',
               existing_type=sa.DATE(),
               nullable=False)
    op.alter_column('course', 'id_timetable',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('course', 'id_programme',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
