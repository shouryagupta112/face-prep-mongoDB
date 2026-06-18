from pydantic import BaseModel

class EmployeeInformation(BaseModel):
    employee_name: str
    designation: str
    salary: float
    branch_id: str