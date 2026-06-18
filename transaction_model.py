from pydantic import BaseModel

class DepositRequest(BaseModel):
    account_number: str
    amount: float


class WithdrawRequest(BaseModel):
    account_number: str
    amount: float


class TransferRequest(BaseModel):
    sender_account: str
    receiver_account: str
    amount: float