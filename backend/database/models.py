from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.orm import mapped_column

from . import Base

class Person(Base):
    __tablename__ = "persons"
    personId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstName: Mapped[str] = mapped_column(String(50), nullable=False)
    lastName: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    employee: Mapped["Employee"] = relationship(back_populates="person", uselist=False)
    hr_employee: Mapped["HREmployee"] = relationship(back_populates="person", uselist=False)
    external_user: Mapped["ExternalUser"] = relationship(back_populates="person", uselist=False)

class Employee(Person):
    __tablename__ = "employees"
    __mapper_args__ = {"polymorphic_identity": "employee"}
    personId: Mapped[int] = mapped_column(Integer, ForeignKey("persons.personId"), primary_key=True)
    roleId: Mapped[int] = mapped_column(Integer, ForeignKey("roles.roleId"), nullable=False)
    hireDate: Mapped[Date] = mapped_column(Date, nullable=False)
    qualifications: Mapped[str] = mapped_column(String(500), nullable=False)
    leave_requests: Mapped[list["LeaveRequest"]] = relationship(back_populates="employee")
    projects: Mapped[list["EmployeeProject"]] = relationship(back_populates="employee")
    role: Mapped["Role"] = relationship(back_populates="employees")
    person: Mapped["Person"] = relationship(back_populates="employee")

class HREmployee(Person):
    __tablename__ = "hr_employees"
    __mapper_args__ = {"polymorphic_identity": "hr_employee"}
    personId: Mapped[int] = mapped_column(Integer, ForeignKey("persons.personId"), primary_key=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    leave_requests: Mapped[list["LeaveRequest"]] = relationship(back_populates="hr_employee")
    external_requests: Mapped[list["ExternalRequest"]] = relationship(back_populates="hr_employee")
    projects: Mapped[list["Project"]] = relationship(back_populates="hr_employee")
    person: Mapped["Person"] = relationship(back_populates="hr_employee")

class ExternalUser(Person):
    __tablename__ = "external_users"
    __mapper_args__ = {"polymorphic_identity": "external_user"}
    personId: Mapped[int] = mapped_column(Integer, ForeignKey("persons.personId"), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    external_requests: Mapped[list["ExternalRequest"]] = relationship(back_populates="external_user")
    person: Mapped["Person"] = relationship(back_populates="external_user")

class Role(Base):
    __tablename__ = "roles"
    roleId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    roleName: Mapped[str] = mapped_column(String(50), nullable=False)
    employees: Mapped[list["Employee"]] = relationship(back_populates="role")

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    requestId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employeeId: Mapped[int] = mapped_column(Integer, ForeignKey("employees.personId"), nullable=False)
    hrEmployeeId: Mapped[int] = mapped_column(Integer, ForeignKey("hr_employees.personId"), nullable=True)
    startDate: Mapped[Date] = mapped_column(Date, nullable=False)
    endDate: Mapped[Date] = mapped_column(Date, nullable=False)
    requestType: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    reason: Mapped[str] = mapped_column(String(500))
    employee: Mapped["Employee"] = relationship(back_populates="leave_requests")
    hr_employee: Mapped["HREmployee"] = relationship(back_populates="leave_requests")

class Project(Base):
    __tablename__ = "projects"
    projectId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    projectName: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    hrEmployeeId: Mapped[int] = mapped_column(Integer, ForeignKey("hr_employees.personId"), nullable=True)
    hr_employee: Mapped["HREmployee"] = relationship(back_populates="projects")
    employees: Mapped[list["EmployeeProject"]] = relationship(back_populates="project")  # Changed to match EmployeeProject.project
    external_requests: Mapped[list["ExternalRequest"]] = relationship(back_populates="project")

class ExternalRequest(Base):
    __tablename__ = "external_requests"
    requestId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userId: Mapped[int] = mapped_column(Integer, ForeignKey("external_users.personId"), nullable=False)
    projectId: Mapped[int] = mapped_column(Integer, ForeignKey("projects.projectId"), nullable=False)
    hrEmployeeId: Mapped[int] = mapped_column(Integer, ForeignKey("hr_employees.personId"), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    response: Mapped[str] = mapped_column(String(500), nullable=True)
    external_user: Mapped["ExternalUser"] = relationship(back_populates="external_requests")
    hr_employee: Mapped["HREmployee"] = relationship(back_populates="external_requests")
    project: Mapped["Project"] = relationship(back_populates="external_requests")

class EmployeeProject(Base):
    __tablename__ = "employee_projects"
    employeeId: Mapped[int] = mapped_column(Integer, ForeignKey("employees.personId"), primary_key=True)
    projectId: Mapped[int] = mapped_column(Integer, ForeignKey("projects.projectId"), primary_key=True)
    employee: Mapped["Employee"] = relationship(back_populates="projects")
    project: Mapped["Project"] = relationship(back_populates="employees")
