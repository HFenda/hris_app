from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class Person(BaseModel):
    personId: Optional[int] = Field(None, description="Unique identifier for the person")
    firstName: str = Field(..., min_length=1, max_length=50, description="Person's first name")
    lastName: str = Field(..., min_length=1, max_length=50, description="Person's last name")
    email: str = Field(..., min_length=5, max_length=255, description="Email address for the person")
    password: str = Field(..., min_length=8, description="Password for authentication")

    class Config:
        arbitrary_types_allowed = True

class Employee(Person):
    employeeId: Optional[int] = Field(None, description="Unique identifier for the employee")
    roleId: int = Field(..., gt=0, description="Reference to the employee's role")
    hireDate: date = Field(..., description="Date when the employee was hired")
    qualifications: str = Field(..., min_length=1, max_length=500, description="Employee's qualifications")

class HREmployee(Person):
    hrEmployeeId: Optional[int] = Field(None, description="Unique identifier for the HR employee")
    department: str = Field(..., min_length=1, max_length=100, description="Department where the HR employee works")

class ExternalUser(Person):
    userId: Optional[int] = Field(None, description="Unique identifier for the external user")
    username: str = Field(..., min_length=3, max_length=50, description="Username for the external user")

class Role(BaseModel):
    roleId: Optional[int] = Field(None, description="Unique identifier for the role")
    roleName: str = Field(..., min_length=1, max_length=50, description="Name of the role")

class LeaveRequest(BaseModel):
    requestId: Optional[int] = Field(None, description="Unique identifier for the leave request")
    employeeId: int = Field(..., gt=0, description="Reference to the requesting employee")
    startDate: date = Field(..., description="Start date of the leave")
    endDate: date = Field(..., description="End date of the leave")
    requestType: str = Field(..., min_length=1, max_length=50, description="Type of leave (e.g., annual, sick)")
    status: str = Field("pending", min_length=1, max_length=20, description="Status of the leave request")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for rejection if applicable")

class Project(BaseModel):
    projectId: Optional[int] = Field(None, description="Unique identifier for the project")
    projectName: str = Field(..., min_length=1, max_length=100, description="Name of the project")
    description: str = Field(..., min_length=1, max_length=500, description="Description of the project")

class ExternalRequest(BaseModel):
    requestId: Optional[int] = Field(None, description="Unique identifier for the external request")
    userId: int = Field(..., gt=0, description="Reference to the external user")
    projectId: int = Field(..., gt=0, description="Reference to the related project")
    description: str = Field(..., min_length=1, max_length=500, description="Description of the external request")
    status: str = Field("pending", min_length=1, max_length=20, description="Status of the external request")
    response: Optional[str] = Field(None, max_length=500, description="HR response to the request")

class EmployeeProject(BaseModel):
    employeeId: int = Field(..., gt=0, description="Reference to the employee")
    projectId: int = Field(..., gt=0, description="Reference to the project")