"""Transaction routes for NEFT, RTGS, IMPS, UPI"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

from validators.ifsc_validator import IFSCValidator
from validators.upi_validator import UPIValidator
from validators.transaction_validator import TransactionValidator

router = APIRouter(prefix="/transactions", tags=["Transactions"])


class TransactionType(str, Enum):
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    UPI = "upi"


class NEFTRequest(BaseModel):
    from_account: str
    to_account: str
    ifsc_code: str = Field(..., min_length=11, max_length=11)
    amount: float = Field(..., gt=0, le=1000000)
    beneficiary_name: str
    remarks: Optional[str] = None
    
    @validator('ifsc_code')
    def validate_ifsc(cls, v):
        if not IFSCValidator.validate(v):
            raise ValueError('Invalid IFSC code')
        return v


class RTGSRequest(BaseModel):
    from_account: str
    to_account: str
    ifsc_code: str = Field(..., min_length=11, max_length=11)
    amount: float = Field(..., ge=200000)  # Min 2 lakh for RTGS
    beneficiary_name: str
    remarks: Optional[str] = None


class IMPSRequest(BaseModel):
    from_account: str
    to_account: str
    ifsc_code: str = Field(..., min_length=11, max_length=11)
    amount: float = Field(..., gt=0, le=500000)
    beneficiary_name: str
    remarks: Optional[str] = None


class UPIRequest(BaseModel):
    from_account: str
    upi_id: str
    amount: float = Field(..., gt=0, le=100000)
    remarks: Optional[str] = None
    
    @validator('upi_id')
    def validate_upi(cls, v):
        if not UPIValidator.validate(v):
            raise ValueError('Invalid UPI ID')
        return v


class TransactionResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float
    timestamp: datetime
    reference_number: str


@router.post("/neft", response_model=TransactionResponse, summary="NEFT Transfer")
async def neft_transfer(request: NEFTRequest):
    """Initiate a NEFT transfer"""
    # Validate transaction
    validation = TransactionValidator.validate_neft(request.amount)
    if not validation['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation['error']
        )
    
    return TransactionResponse(
        transaction_id="NEFT" + datetime.now().strftime("%Y%m%d%H%M%S"),
        status="initiated",
        amount=request.amount,
        timestamp=datetime.now(),
        reference_number="REF" + datetime.now().strftime("%Y%m%d%H%M%S")
    )


@router.post("/rtgs", response_model=TransactionResponse, summary="RTGS Transfer")
async def rtgs_transfer(request: RTGSRequest):
    """Initiate a RTGS transfer (min ₹2,00,000)"""
    validation = TransactionValidator.validate_rtgs(request.amount)
    if not validation['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation['error']
        )
    
    return TransactionResponse(
        transaction_id="RTGS" + datetime.now().strftime("%Y%m%d%H%M%S"),
        status="initiated",
        amount=request.amount,
        timestamp=datetime.now(),
        reference_number="REF" + datetime.now().strftime("%Y%m%d%H%M%S")
    )


@router.post("/imps", response_model=TransactionResponse, summary="IMPS Transfer")
async def imps_transfer(request: IMPSRequest):
    """Initiate an IMPS transfer (instant)"""
    validation = TransactionValidator.validate_imps(request.amount)
    if not validation['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation['error']
        )
    
    return TransactionResponse(
        transaction_id="IMPS" + datetime.now().strftime("%Y%m%d%H%M%S"),
        status="success",
        amount=request.amount,
        timestamp=datetime.now(),
        reference_number="REF" + datetime.now().strftime("%Y%m%d%H%M%S")
    )


@router.post("/upi", response_model=TransactionResponse, summary="UPI Payment")
async def upi_payment(request: UPIRequest):
    """Initiate a UPI payment"""
    validation = TransactionValidator.validate_upi(request.amount)
    if not validation['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation['error']
        )
    
    return TransactionResponse(
        transaction_id="UPI" + datetime.now().strftime("%Y%m%d%H%M%S"),
        status="success",
        amount=request.amount,
        timestamp=datetime.now(),
        reference_number="REF" + datetime.now().strftime("%Y%m%d%H%M%S")
    )


@router.get("/history", summary="Get transaction history")
async def get_transaction_history(
    account_number: Optional[str] = None,
    transaction_type: Optional[TransactionType] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = 50
):
    """Get transaction history with filters"""
    return {
        "transactions": [],
        "total_count": 0,
        "page": 1,
        "limit": limit
    }
