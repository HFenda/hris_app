from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from backend import get_current_user, check_permission, CurrentUserContext
from ..database import get_db
from backend.database.models import Role

router = APIRouter(prefix="/roles", tags=["Role Management"])

@router.get("/")
async def get_all_roles(
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "view_all_employees")  # Or "manage_roles"
    return db.query(Role).all()

@router.post("/")
async def create_role(
    roleName: str,
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "create_employee")

    new_role = Role(roleName=roleName)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return {"message": "Role created", "role": new_role}

@router.put("/{role_id}")
async def update_role(
    role_id: int = Path(..., description="ID of the role to update"),
    roleName: str = None,
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "edit_employee")

    role = db.query(Role).filter(Role.roleId == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if roleName is not None:
        role.roleName = roleName

    db.commit()
    db.refresh(role)
    return {"message": "Role updated", "role": role}

@router.delete("/{role_id}")
async def delete_role(
    role_id: int = Path(..., description="ID of the role to delete"),
    current: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_permission(current, "delete_employee")

    role = db.query(Role).filter(Role.roleId == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    db.delete(role)
    db.commit()
    return {"message": "Role deleted", "role_id": role_id}
