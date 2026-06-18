from fastapi import FastAPI, HTTPException
from bson import ObjectId
from datetime import datetime
import random

from database import *

from customer_model import CustomerProfile
from account_model import AccountInformation
from branch_model import BranchInformation
from employee_model import EmployeeInformation

from transaction_model import (
    DepositRequest,
    WithdrawRequest,
    TransferRequest
)

app = FastAPI(
    title="Banking Management System",
    description="Backend API for managing bank operations",
    version="1.0"
)

# =====================================================
# CUSTOMER SECTION
# =====================================================

@app.post("/customers")
def register_new_customer(customer_profile: CustomerProfile):

    saved_customer = customer_collection.insert_one(
        customer_profile.dict()
    )

    return {
        "message": "Customer registered successfully",
        "customer_id": str(saved_customer.inserted_id)
    }


@app.get("/customers")
def show_all_customers():

    customer_list = []

    for customer in customer_collection.find():
        customer["_id"] = str(customer["_id"])
        customer_list.append(customer)

    return customer_list


@app.put("/customers/{customer_id}")
def update_customer_details(
        customer_id: str,
        customer_profile: CustomerProfile
):

    customer_collection.update_one(
        {"_id": ObjectId(customer_id)},
        {"$set": customer_profile.dict()}
    )

    return {"message": "Customer information updated"}


@app.delete("/customers/{customer_id}")
def remove_customer_record(customer_id: str):

    customer_collection.delete_one(
        {"_id": ObjectId(customer_id)}
    )

    return {"message": "Customer removed successfully"}


# =====================================================
# ACCOUNT SECTION
# =====================================================

@app.post("/accounts")
def open_new_account(account_information: AccountInformation):

    generated_account_number = (
        "ACC" + str(random.randint(10000, 99999))
    )

    account_data = {
        "account_number": generated_account_number,
        "customer_id": account_information.customer_id,
        "account_type": account_information.account_type,
        "current_balance": account_information.opening_balance
    }

    account_collection.insert_one(account_data)

    return {
        "message": "Account created successfully",
        "account_number": generated_account_number
    }


@app.get("/accounts")
def show_all_accounts():

    account_list = []

    for account in account_collection.find():
        account["_id"] = str(account["_id"])
        account_list.append(account)

    return account_list


@app.delete("/accounts/{account_number}")
def close_existing_account(account_number: str):

    account_collection.delete_one(
        {"account_number": account_number}
    )

    return {
        "message": "Account closed successfully"
    }


# =====================================================
# BRANCH SECTION
# =====================================================

@app.post("/branches")
def add_new_branch(branch_information: BranchInformation):

    saved_branch = branch_collection.insert_one(
        branch_information.dict()
    )

    return {
        "message": "Branch added successfully",
        "branch_id": str(saved_branch.inserted_id)
    }


@app.get("/branches")
def show_all_branches():

    branch_list = []

    for branch in branch_collection.find():
        branch["_id"] = str(branch["_id"])
        branch_list.append(branch)

    return branch_list


# =====================================================
# EMPLOYEE SECTION
# =====================================================

@app.post("/employees")
def add_new_employee(employee_information: EmployeeInformation):

    saved_employee = employee_collection.insert_one(
        employee_information.dict()
    )

    return {
        "message": "Employee added successfully",
        "employee_id": str(saved_employee.inserted_id)
    }


@app.get("/employees")
def show_all_employees():

    employee_list = []

    for employee in employee_collection.find():
        employee["_id"] = str(employee["_id"])
        employee_list.append(employee)

    return employee_list


@app.delete("/employees/{employee_id}")
def remove_employee(employee_id: str):

    employee_collection.delete_one(
        {"_id": ObjectId(employee_id)}
    )

    return {
        "message": "Employee removed successfully"
    }


# =====================================================
# DEPOSIT MONEY
# =====================================================

@app.post("/deposit")
def add_money_to_account(deposit_request: DepositRequest):

    account = account_collection.find_one(
        {"account_number": deposit_request.account_number}
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    updated_balance = (
        account["current_balance"] +
        deposit_request.amount
    )

    account_collection.update_one(
        {"account_number": deposit_request.account_number},
        {"$set": {"current_balance": updated_balance}}
    )

    transaction_collection.insert_one({
        "account_number": deposit_request.account_number,
        "transaction_type": "Deposit",
        "amount": deposit_request.amount,
        "transaction_time": datetime.now()
    })

    return {
        "message": "Money deposited successfully",
        "updated_balance": updated_balance
    }


# =====================================================
# WITHDRAW MONEY
# =====================================================

@app.post("/withdraw")
def take_money_from_account(
        withdraw_request: WithdrawRequest
):

    account = account_collection.find_one(
        {"account_number": withdraw_request.account_number}
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if account["current_balance"] < withdraw_request.amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    updated_balance = (
        account["current_balance"] -
        withdraw_request.amount
    )

    account_collection.update_one(
        {"account_number": withdraw_request.account_number},
        {"$set": {"current_balance": updated_balance}}
    )

    transaction_collection.insert_one({
        "account_number": withdraw_request.account_number,
        "transaction_type": "Withdrawal",
        "amount": withdraw_request.amount,
        "transaction_time": datetime.now()
    })

    return {
        "message": "Withdrawal completed",
        "updated_balance": updated_balance
    }


# =====================================================
# TRANSFER MONEY
# =====================================================

@app.post("/transfer")
def transfer_money_between_accounts(
        transfer_request: TransferRequest
):

    sender_account = account_collection.find_one(
        {"account_number": transfer_request.sender_account}
    )

    receiver_account = account_collection.find_one(
        {"account_number": transfer_request.receiver_account}
    )

    if not sender_account:
        raise HTTPException(
            status_code=404,
            detail="Sender account not found"
        )

    if not receiver_account:
        raise HTTPException(
            status_code=404,
            detail="Receiver account not found"
        )

    if sender_account["current_balance"] < transfer_request.amount:
        raise HTTPException(
            status_code=400,
            detail="Not enough balance"
        )

    sender_new_balance = (
        sender_account["current_balance"]
        - transfer_request.amount
    )

    receiver_new_balance = (
        receiver_account["current_balance"]
        + transfer_request.amount
    )

    account_collection.update_one(
        {"account_number": transfer_request.sender_account},
        {"$set": {"current_balance": sender_new_balance}}
    )

    account_collection.update_one(
        {"account_number": transfer_request.receiver_account},
        {"$set": {"current_balance": receiver_new_balance}}
    )

    transaction_collection.insert_one({
        "account_number": transfer_request.sender_account,
        "transaction_type": "Transfer Sent",
        "amount": transfer_request.amount,
        "transaction_time": datetime.now()
    })

    transaction_collection.insert_one({
        "account_number": transfer_request.receiver_account,
        "transaction_type": "Transfer Received",
        "amount": transfer_request.amount,
        "transaction_time": datetime.now()
    })

    return {
        "message": "Transfer completed successfully"
    }


# =====================================================
# TRANSACTION HISTORY
# =====================================================

@app.get("/transactions/{account_number}")
def show_transaction_history(account_number: str):

    history = []

    for transaction in transaction_collection.find(
            {"account_number": account_number}
    ):
        transaction["_id"] = str(transaction["_id"])
        history.append(transaction)

    return history


# =====================================================
# SEARCH CUSTOMER BY NAME
# =====================================================

@app.get("/customer-search/{customer_name}")
def search_customer_by_name(customer_name: str):

    matching_customers = []

    for customer in customer_collection.find(
            {"customer_name": customer_name}
    ):
        customer["_id"] = str(customer["_id"])
        matching_customers.append(customer)

    return matching_customers


# =====================================================
# ROOT API
# =====================================================

@app.get("/")
def welcome_message():

    return {
        "project": "Banking Management System",
        "status": "Running Successfully"
    }