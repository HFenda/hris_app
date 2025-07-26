from .employee_routes import router as employees
from .hr_routes import router as hr
from .external_routes import router as external
from .leave_routes import router as leave
from .project_routes import router as project
from .role_routes import router as role

__all__ = [
    "employee_routes",
    "hr_routes",
    "external_routes",
    "leave_routes",
    "project_routes",
    "role_routes",
]