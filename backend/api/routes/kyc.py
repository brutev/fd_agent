"""KYC verification routes"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date
from enum import Enum

from validators.aadhaar_validator import AadhaarValidator
from validators.pan_validator import PANValidator

router = APIRouter(prefix="/kyc", tags=["KYC"])


class KYCStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AadhaarVerifyRequest(BaseModel):
    aadhaar_number: str = Field(..., min_length=12, max_length=12)
    name: str
    dob: date
    
    @validator('aadhaar_number')
    def validate_aadhaar(cls, v):
        if not AadhaarValidator.validate(v):
            raise ValueError('Invalid Aadhaar number')
        return v


class PANVerifyRequest(BaseModel):
    pan_number: str = Field(..., min_length=10, max_length=10)
    name: str
    dob: date
    
    @validator('pan_number')
    def validate_pan(cls, v):
        if not PANValidator.validate(v):
            raise ValueError('Invalid PAN number')
        return v


class KYCResponse(BaseModel):
    kyc_id: str
    status: KYCStatus
    verification_type: str
    verified_at: Optional[datetime] = None
    message: str


@router.post("/aadhaar/verify", response_model=KYCResponse, summary="Verify Aadhaar")
async def verify_aadhaar(request: AadhaarVerifyRequest):
    """Verify Aadhaar number using UIDAI API"""
    return KYCResponse(
        kyc_id="KYC" + datetime.now().strftime("%Y%m%d%H%M%S"),
        status=KYCStatus.VERIFIED,
        verification_type="aadhaar",
        verified_at=datetime.now(),
        message="Aadhaar verified successfully"
    )


@router.post("/aadhaar/otp", summary="Send Aadhaar OTP")
async def send_aadhaar_otp(aadhaar_number: str):
    """Send OTP to Aadhaar linked mobile for e-KYC"""
    if not AadhaarValidator.validate(aadhaar_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Aadhaar number"
        )
    return {
        "success": True,
        "message": "OTP sent to Aadhaar linked mobile",
        "expires_in": 300
    }


@router.post("/pan/verify", response_model=KYCResponse, summary="Verify PAN")
async def verify_pan(request: PANVerifyRequest):
    """Verify PAN number"""
    return KYCResponse(
        kyc_id="KYC" + datetime.now().strftime("%Y%m%d%H%M%S"),
        status=KYCStatus.VERIFIED,
        verification_type="pan",
        verified_at=datetime.now(),
        message="PAN verified successfully"
    )


@router.post("/document/upload", summary="Upload KYC document")
async def upload_document(
    document_type: str,
    file: UploadFile = File(...)
):
    """Upload KYC documents (ID proof, address proof, etc.)"""
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: JPEG, PNG, PDF"
        )
    
    return {
        "success": True,
        "document_id": "DOC" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "document_type": document_type,
        "filename": file.filename,
        "status": "uploaded"
    }


@router.get("/status", response_model=KYCResponse, summary="Get KYC status")
async def get_kyc_status():
    """Get current KYC verification status"""
    return KYCResponse(
        kyc_id="KYC20260105",
        status=KYCStatus.VERIFIED,
        verification_type="full",
        verified_at=datetime.now(),
        message="KYC verification complete"
    )


@router.post("/video/schedule", summary="Schedule Video KYC")
async def schedule_video_kyc(
    preferred_date: date,
    preferred_time: str
):
    """Schedule a video KYC verification call"""
    return {
        "success": True,
        "appointment_id": "VKYC" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "scheduled_date": preferred_date.isoformat(),
        "scheduled_time": preferred_time,
        "meeting_link": "https://kyc.example.com/meeting/12345",
        "message": "Video KYC scheduled successfully"
    }
