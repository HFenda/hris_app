from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from backend import get_current_user, check_permission, CurrentUserContext
from ..database import get_db
from backend.database.models import LeaveRequest

router = APIRouter(prefix="/leaves", tags=["Leave Management"])

# Employee: View own leave requests
@router.get("/me")
async def view_my_leave_requests(
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "view_all_leave_requests")
    return db.query(LeaveRequest).filter(LeaveRequest.employeeId == current.user.personId).all()

# Employee: Submit a new leave request
@router.post("/")
async def submit_leave_request(
    startDate: date,
    endDate: date,
    requestType: str,
    reason: str = None,
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "send_leave_request")

    leave_request = LeaveRequest(
        employeeId=current.user.personId,
        startDate=startDate,
        endDate=endDate,
        requestType=requestType,
        reason=reason,
        status="pending"
    )

    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)

    return {"message": "Leave request submitted", "request": leave_request}

# HR: View all leave requests
@router.get("/all")
async def view_all_leave_requests(
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "view_all_leave_requests")
    return db.query(LeaveRequest).all()

# HR: Approve or deny a leave request
@router.post("/{request_id}/respond")
async def respond_to_leave_request(
    request_id: int,
    status: str,
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "approve_deny_leave_requests")

    if status not in ["approved", "denied"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'denied'")

    leave_request = db.query(LeaveRequest).filter(LeaveRequest.requestId == request_id).first()
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave_request.status = status
    leave_request.hrEmployeeId = current.user.personId

    db.commit()
    return {"message": f"Leave request {status}", "request_id": request_id}
