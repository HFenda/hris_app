from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import get_current_user, check_permission, CurrentUserContext
from backend.database import get_db
from backend.database.models import ExternalRequest, Project, Employee

router = APIRouter(prefix="/employee", tags=["Employee"])

@router.get("/dashboard")
async def employee_dashboard(
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current.role != "employee":
        raise HTTPException(status_code=403, detail="Not authorized")

    assigned_projects = [ep.project for ep in current.user.projects]

    return {
        "user": {
            "name": f"{current.user.firstName} {current.user.lastName}",
            "email": current.user.email,
        },
        "assigned_projects": assigned_projects
    }

@router.get("/me")
async def view_personal_info(
    current: CurrentUserContext = Depends(get_current_user)
):
    check_permission(current, "view_personal_info")

    return {
        "firstName": current.user.firstName,
        "lastName": current.user.lastName,
        "email": current.user.email,
        "hireDate": current.user.hireDate,
        "qualifications": current.user.qualifications,
        "role": current.user.role.roleName if current.user.role else None
    }
