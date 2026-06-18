from pydantic import BaseModel

class CustomerProfile(BaseModel):
    customer_name: str
    email: str
    phone_number: str
    city: str