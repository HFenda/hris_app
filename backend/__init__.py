from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .database import SessionLocal, get_db
from sqlalchemy.orm import Session
from backend.auth.security import hash_password, verify_password
from .database.models import Employee, HREmployee, ExternalUser, Role, Project, Person, LeaveRequest, EmployeeProject, ExternalRequest
import sqlalchemy
from typing import Any

app = FastAPI()

# === JWT Configuration ===
SECRET_KEY = "your-secret-key"  # Replace with a secure key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# === User Context and Permissions ===

class CurrentUserContext:
    def __init__(self, user: Any, role: str, permissions: dict):
        self.user = user
        self.role = role
        self.permissions = permissions

def check_permission(current: CurrentUserContext, permission: str):
    if not current.permissions.get(permission, False):
        raise HTTPException(status_code=403, detail="Permission denied")

# === DB Dependency ===

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === JWT Creation ===

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# === Authenticated User Dependency ===

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> CurrentUserContext:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        role = payload.get("role")
    except JWTError:
        raise credentials_exception


    if role == "hr":
        user = db.query(HREmployee).filter(HREmployee.email == username).first()
    elif role == "external":
        user = db.query(ExternalUser).filter(ExternalUser.email == username).first()
    elif role == "employee":
        user = db.query(Employee).filter(Employee.email == username).first()
    else:
        user = db.query(Person).filter(Person.email == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Define permissions
    permissions = {}
    if isinstance(user, Employee):
        permissions = {
            "view_personal_info": True,
            "send_leave_request": True,
            "view_all_leave_requests": True,
            "view_all_projects": True
        }
    elif isinstance(user, HREmployee):
        permissions = {
            "view_all_employees": True,
            "create_employee": True,
            "edit_employee": True,
            "delete_employee": True,
            "view_all_leave_requests": True,
            "approve_deny_leave_requests": True,
            "view_all_external_requests": True,
            "respond_to_external_requests": True,
            "view_all_projects": True,
            "create_project": True,
            "edit_project": True,
            "delete_project": True,
            "view_all_projects": True
        }
    elif isinstance(user, ExternalUser):
        permissions = {
            "view_own_projects": True,
            "send_request": True,
            "view_projects": True
        }

    return CurrentUserContext(user=user, role=role, permissions=permissions)

# === Import and Include Routers ===

from .routes import employees as employees_router
from .routes import hr as hr_router
from .routes import external as external_router
from .routes import leave as leave_router
from .routes import project as project_router
from .routes import role as role_router

app.include_router(employees_router)
app.include_router(hr_router)
app.include_router(external_router)
app.include_router(leave_router)
app.include_router(project_router)
app.include_router(role_router)

# === Register Endpoint ===

@app.post("/register", tags=["User Management"])
async def register(firstName: str, lastName: str, email: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(Person).filter(Person.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(password)

    if email.endswith("@company.ba"):
        user = HREmployee(firstName=firstName, lastName=lastName, email=email, password=hashed_pwd, department="HR" if "hr" in email.lower() else "Default")
    else:
        user = ExternalUser(
            firstName=firstName,
            lastName=lastName,
            email=email,
            password=hashed_pwd,
            username=email.split("@")[0]
        )

    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully", "user_id": user.personId}

# === Login Endpoint ===

@app.post("/login", tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username
    password = form_data.password

    user = (
        db.query(HREmployee).filter(HREmployee.email == email).first()
        or db.query(ExternalUser).filter(ExternalUser.email == email).first()
        or db.query(Employee).filter(Employee.email == email).first()
    )

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    role = "employee" if isinstance(user, Employee) else "hr" if isinstance(user, HREmployee) else "external"
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": email, "role": role}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}
