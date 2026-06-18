from pydantic import BaseModel

class BranchInformation(BaseModel):
    branch_name: str
    branch_code: str
    city: str