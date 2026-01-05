"""Authentication routes for the FD Agent System"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])


class SendOTPRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r"^[6-9]\d{9}$", description="Indian mobile number")


class VerifyOTPRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r"^[6-9]\d{9}$")
    otp: str = Field(..., min_length=6, max_length=6)


class LoginRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r"^[6-9]\d{9}$")
    mpin: str = Field(..., min_length=4, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class SetMPINRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r"^[6-9]\d{9}$")
    mpin: str = Field(..., min_length=4, max_length=6)
    confirm_mpin: str = Field(..., min_length=4, max_length=6)


@router.post("/send-otp", summary="Send OTP to mobile number")
async def send_otp(request: SendOTPRequest):
    """Send OTP to the given mobile number for verification"""
    # In production, integrate with SMS gateway
    return {
        "success": True,
        "message": f"OTP sent to {request.mobile_number}",
        "expires_in": 300  # 5 minutes
    }


@router.post("/verify-otp", summary="Verify OTP")
async def verify_otp(request: VerifyOTPRequest):
    """Verify the OTP sent to mobile number"""
    # In production, validate against stored OTP
    return {
        "success": True,
        "verified": True,
        "message": "OTP verified successfully"
    }


@router.post("/login", response_model=TokenResponse, summary="User login")
async def login(request: LoginRequest):
    """Login with mobile number and MPIN"""
    # In production, validate credentials against database
    return TokenResponse(
        access_token="sample_access_token",
        refresh_token="sample_refresh_token",
        expires_in=1800  # 30 minutes
    )


@router.post("/refresh-token", response_model=TokenResponse, summary="Refresh access token")
async def refresh_token(refresh_token: str):
    """Refresh the access token using refresh token"""
    return TokenResponse(
        access_token="new_access_token",
        refresh_token="new_refresh_token",
        expires_in=1800
    )


@router.post("/set-mpin", summary="Set MPIN for user")
async def set_mpin(request: SetMPINRequest):
    """Set or update MPIN for user authentication"""
    if request.mpin != request.confirm_mpin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MPIN and confirm MPIN do not match"
        )
    return {
        "success": True,
        "message": "MPIN set successfully"
    }
