from pydantic import BaseModel

class AccountInformation(BaseModel):
    customer_id: str
    account_type: str
    opening_balance: float