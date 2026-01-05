"""Account management routes"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/accounts", tags=["Accounts"])


class AccountType(str, Enum):
    SAVINGS = "savings"
    CURRENT = "current"
    FIXED_DEPOSIT = "fd"


class Account(BaseModel):
    account_number: str
    account_type: AccountType
    balance: float
    currency: str = "INR"
    status: str = "active"


class AccountStatement(BaseModel):
    transaction_id: str
    date: datetime
    description: str
    amount: float
    balance: float
    type: str  # credit/debit


@router.get("/", response_model=List[Account], summary="Get all accounts")
async def get_accounts():
    """Get all accounts for the authenticated user"""
    return [
        Account(
            account_number="1234567890",
            account_type=AccountType.SAVINGS,
            balance=50000.00,
            status="active"
        )
    ]


@router.get("/{account_number}", response_model=Account, summary="Get account details")
async def get_account(account_number: str):
    """Get details of a specific account"""
    return Account(
        account_number=account_number,
        account_type=AccountType.SAVINGS,
        balance=50000.00,
        status="active"
    )


@router.get("/{account_number}/balance", summary="Get account balance")
async def get_balance(account_number: str):
    """Get current balance of an account"""
    return {
        "account_number": account_number,
        "balance": 50000.00,
        "currency": "INR",
        "as_of": datetime.now().isoformat()
    }


@router.get("/{account_number}/statement", response_model=List[AccountStatement], summary="Get account statement")
async def get_statement(
    account_number: str,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = 50
):
    """Get account statement for a date range"""
    return [
        AccountStatement(
            transaction_id="TXN001",
            date=datetime.now(),
            description="UPI Payment",
            amount=-500.00,
            balance=49500.00,
            type="debit"
        )
    ]
