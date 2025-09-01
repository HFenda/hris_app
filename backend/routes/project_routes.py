from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import get_current_user, check_permission, CurrentUserContext
from ..database import get_db
from backend.database.models import Project, EmployeeProject

router = APIRouter(prefix="/projects", tags=["Project Management"])

# HR: Create a new project
@router.post("/")
async def create_project(
    projectName: str,
    description: str,
    hrEmployeeId: int = None,  # Optional field
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "create_project")

    project = Project(
        projectName=projectName,
        description=description,
        hrEmployeeId=hrEmployeeId
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return {"message": "Project created", "project": project}

# Employee: View assigned projects
@router.get("/me")
async def view_my_projects(
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current.role != "employee":
        raise HTTPException(status_code=403, detail="Not authorized")

    assignments = db.query(EmployeeProject).filter(EmployeeProject.employeeId == current.user.personId).all()
    return [db.query(Project).filter(Project.projectId == ap.projectId).first() for ap in assignments]

# HR: Update a project
@router.put("/{project_id}")
async def update_project(
    project_id: int,
    projectName: str = None,
    description: str = None,
    hrEmployeeId: int = None,
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "edit_project")

    project = db.query(Project).filter(Project.projectId == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if projectName is not None:
        project.projectName = projectName
    if description is not None:
        project.description = description
    if hrEmployeeId is not None:
        project.hrEmployeeId = hrEmployeeId

    db.commit()
    db.refresh(project)
    return {"message": "Project updated", "project": project}

# HR: Delete a project
@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "delete_project")

    project = db.query(Project).filter(Project.projectId == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted", "project_id": project_id}

@router.get("/projects")
async def get_all_projects(
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current.role not in ("external","hr"):
        raise HTTPException(status_code=403, detail="Not authorized")

    return db.query(Project).all()