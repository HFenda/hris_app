from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import get_current_user, check_permission, CurrentUserContext
from ..database import get_db
from backend.database.models import ExternalRequest, Project

router = APIRouter(prefix="/external", tags=["External User"])

# External User Dashboard
@router.get("/dashboard")
async def external_user_dashboard(
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current.role != "external":
        raise HTTPException(status_code=403, detail="Not authorized")

    projects = db.query(Project).all()
    requests = db.query(ExternalRequest).filter(ExternalRequest.userId == current.user.personId).all()

    return {
        "user": {
            "name": f"{current.user.firstName} {current.user.lastName}",
            "email": current.user.email,
        },
        "projects": projects,
        "my_requests": requests
    }

# External User: View own requests
@router.get("/requests/me")
async def get_external_user_requests(
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "send_request")
    return db.query(ExternalRequest).filter(ExternalRequest.userId == current.user.personId).all()

# External User: Create a new request
@router.post("/requests")
async def create_external_user_request(
    projectId: int,
    description: str,
    db: Session = Depends(get_db),
    current: CurrentUserContext = Depends(get_current_user)
):
    check_permission(current, "send_request")

    new_request = ExternalRequest(
        userId=current.user.personId,
        projectId=projectId,
        description=description,
        status="pending"
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {
        "message": "External request submitted successfully.",
        "request": new_request
    }
