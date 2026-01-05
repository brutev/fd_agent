"""Loan management routes"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from enum import Enum

router = APIRouter(prefix="/loans", tags=["Loans"])


class LoanType(str, Enum):
    PERSONAL = "personal"
    HOME = "home"
    CAR = "car"
    EDUCATION = "education"
    BUSINESS = "business"


class LoanStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    CLOSED = "closed"


class LoanApplicationRequest(BaseModel):
    loan_type: LoanType
    amount: float = Field(..., gt=10000)
    tenure_months: int = Field(..., ge=6, le=360)
    purpose: str
    monthly_income: float = Field(..., gt=0)
    employer_name: Optional[str] = None


class EMICalculationRequest(BaseModel):
    principal: float = Field(..., gt=0)
    interest_rate: float = Field(..., gt=0, le=30)
    tenure_months: int = Field(..., ge=1, le=360)


class EMIResponse(BaseModel):
    monthly_emi: float
    total_interest: float
    total_amount: float
    principal: float
    interest_rate: float
    tenure_months: int


class LoanApplicationResponse(BaseModel):
    application_id: str
    loan_type: LoanType
    amount: float
    status: LoanStatus
    created_at: datetime
    estimated_emi: float


class AmortizationEntry(BaseModel):
    month: int
    emi: float
    principal: float
    interest: float
    balance: float


@router.post("/apply", response_model=LoanApplicationResponse, summary="Apply for loan")
async def apply_for_loan(request: LoanApplicationRequest):
    """Submit a loan application"""
    # Calculate estimated EMI
    rate = 0.10 / 12  # 10% annual rate
    emi = (request.amount * rate * (1 + rate)**request.tenure_months) / ((1 + rate)**request.tenure_months - 1)
    
    return LoanApplicationResponse(
        application_id="LOAN" + datetime.now().strftime("%Y%m%d%H%M%S"),
        loan_type=request.loan_type,
        amount=request.amount,
        status=LoanStatus.PENDING,
        created_at=datetime.now(),
        estimated_emi=round(emi, 2)
    )


@router.post("/emi-calculator", response_model=EMIResponse, summary="Calculate EMI")
async def calculate_emi(request: EMICalculationRequest):
    """Calculate EMI for a loan"""
    monthly_rate = request.interest_rate / 100 / 12
    n = request.tenure_months
    
    if monthly_rate == 0:
        emi = request.principal / n
    else:
        emi = (request.principal * monthly_rate * (1 + monthly_rate)**n) / ((1 + monthly_rate)**n - 1)
    
    total_amount = emi * n
    total_interest = total_amount - request.principal
    
    return EMIResponse(
        monthly_emi=round(emi, 2),
        total_interest=round(total_interest, 2),
        total_amount=round(total_amount, 2),
        principal=request.principal,
        interest_rate=request.interest_rate,
        tenure_months=n
    )


@router.post("/amortization", response_model=List[AmortizationEntry], summary="Get amortization schedule")
async def get_amortization_schedule(request: EMICalculationRequest):
    """Get complete amortization schedule for a loan"""
    monthly_rate = request.interest_rate / 100 / 12
    n = request.tenure_months
    
    if monthly_rate == 0:
        emi = request.principal / n
    else:
        emi = (request.principal * monthly_rate * (1 + monthly_rate)**n) / ((1 + monthly_rate)**n - 1)
    
    schedule = []
    balance = request.principal
    
    for month in range(1, n + 1):
        interest = balance * monthly_rate
        principal_payment = emi - interest
        balance = balance - principal_payment
        
        schedule.append(AmortizationEntry(
            month=month,
            emi=round(emi, 2),
            principal=round(principal_payment, 2),
            interest=round(interest, 2),
            balance=round(max(0, balance), 2)
        ))
    
    return schedule


@router.get("/eligibility", summary="Check loan eligibility")
async def check_eligibility(
    loan_type: LoanType,
    monthly_income: float,
    existing_emi: float = 0
):
    """Check loan eligibility based on income and existing obligations"""
    # FOIR (Fixed Obligation to Income Ratio) should be <= 50%
    available_income = monthly_income * 0.5 - existing_emi
    
    # Estimate maximum loan at 10% interest for 60 months
    rate = 0.10 / 12
    n = 60
    max_loan = available_income * ((1 + rate)**n - 1) / (rate * (1 + rate)**n)
    
    return {
        "eligible": available_income > 0,
        "max_loan_amount": round(max(0, max_loan), 2),
        "max_emi": round(max(0, available_income), 2),
        "foir_available": round(available_income / monthly_income * 100, 2) if monthly_income > 0 else 0,
        "loan_type": loan_type
    }


@router.get("/applications", summary="Get loan applications")
async def get_applications():
    """Get all loan applications for the user"""
    return {
        "applications": [],
        "total_count": 0
    }


@router.get("/applications/{application_id}", summary="Get application status")
async def get_application_status(application_id: str):
    """Get status of a specific loan application"""
    return {
        "application_id": application_id,
        "status": LoanStatus.PENDING,
        "message": "Application is under review"
    }
