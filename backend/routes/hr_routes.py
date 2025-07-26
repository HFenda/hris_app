from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from backend import get_current_user, check_permission, CurrentUserContext, hash_password
from backend.database import get_db
from backend.database.models import Project, ExternalRequest, Employee, Role

router = APIRouter(prefix="/hr", tags=["HR"])

@router.get("/dashboard")
async def hr_dashboard(
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current.role != "hr":
        raise HTTPException(status_code=403, detail="Not authorized")

    assigned_projects = db.query(Project).filter(Project.hrEmployeeId == current.user.personId).all()
    external_requests = db.query(ExternalRequest).filter(ExternalRequest.hrEmployeeId == current.user.personId).all()

    return {
        "user": {
            "name": f"{current.user.firstName} {current.user.lastName}",
            "email": current.user.email,
        },
        "assigned_projects": assigned_projects,
        "incoming_requests": external_requests
    }

@router.get("/external-requests")
async def get_all_external_requests(
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "view_all_external_requests")

    return db.query(ExternalRequest).all()

@router.post("/external-requests/{request_id}/respond")
async def respond_to_external_request(
    request_id: int,
    response: str,
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "respond_to_external_requests")

    external_request = db.query(ExternalRequest).filter(ExternalRequest.requestId == request_id).first()
    if not external_request:
        raise HTTPException(status_code=404, detail="Request not found")

    external_request.response = response
    external_request.status = "responded"
    external_request.hrEmployeeId = current.user.personId

    db.commit()
    return {"message": "Response sent", "request_id": request_id}

@router.get("/employees")
async def get_all_employees(
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "view_all_employees")
    return db.query(Employee).all()

@router.post("/employees")
async def create_employee(
    firstName: str,
    lastName: str,
    email: str,
    password: str,
    roleId: int,
    hireDate: date,
    qualifications: str,
    db: Session = Depends(get_db),
    current: CurrentUserContext = Depends(get_current_user)
):
    check_permission(current, "create_employee")

    from backend.database.models import Person

    existing = db.query(Person).filter(Person.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pwd = hash_password(password)
    employee = Employee(
        firstName=firstName,
        lastName=lastName,
        email=email,
        password=hashed_pwd,
        roleId=roleId,
        hireDate=hireDate,
        qualifications=qualifications
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

@router.put("/employees/{employee_id}")
async def update_employee(
    employee_id: int,
    firstName: str = None,
    lastName: str = None,
    email: str = None,
    roleId: int = None,
    hireDate: date = None,
    qualifications: str = None,
    db: Session = Depends(get_db),
    current: CurrentUserContext = Depends(get_current_user)
):
    check_permission(current, "edit_employee")
    employee = db.query(Employee).filter(Employee.personId == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if firstName: employee.firstName = firstName
    if lastName: employee.lastName = lastName
    if email: employee.email = email
    if roleId: employee.roleId = roleId
    if hireDate: employee.hireDate = hireDate
    if qualifications: employee.qualifications = qualifications

    db.commit()
    db.refresh(employee)
    return employee

@router.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current: CurrentUserContext = Depends(get_current_user)
):
    check_permission(current, "delete_employee")
    employee = db.query(Employee).filter(Employee.personId == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted successfully"}