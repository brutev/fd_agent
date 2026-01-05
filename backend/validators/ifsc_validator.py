import re
from typing import Optional

class IFSCValidator:
    """IFSC Code validator following Indian banking standards"""
    
    @staticmethod
    def validate(ifsc: str) -> bool:
        """Validate IFSC code format: 4 letters + 7 alphanumeric"""
        if not ifsc or len(ifsc) != 11:
            return False
        
        pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        return bool(re.match(pattern, ifsc.upper()))
    
    @staticmethod
    def get_bank_code(ifsc: str) -> Optional[str]:
        """Extract bank code from IFSC"""
        if IFSCValidator.validate(ifsc):
            return ifsc[:4].upper()
        return None

class PANValidator:
    """PAN Card validator with checksum verification"""
    
    @staticmethod
    def validate(pan: str) -> bool:
        """Validate PAN format: 5 letters + 4 digits + 1 letter"""
        if not pan or len(pan) != 10:
            return False
        
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        return bool(re.match(pattern, pan.upper()))

class AadhaarValidator:
    """Aadhaar validator with Verhoeff algorithm"""
    
    VERHOEFF_TABLE_D = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]
    
    VERHOEFF_TABLE_P = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]
    
    VERHOEFF_TABLE_INV = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
    
    @staticmethod
    def validate(aadhaar: str) -> bool:
        """Validate Aadhaar using Verhoeff algorithm"""
        if not aadhaar or len(aadhaar) != 12:
            return False
        
        if not aadhaar.isdigit():
            return False
        
        # Verhoeff checksum validation
        c = 0
        for i, digit in enumerate(reversed(aadhaar)):
            c = AadhaarValidator.VERHOEFF_TABLE_D[c][
                AadhaarValidator.VERHOEFF_TABLE_P[(i + 1) % 8][int(digit)]
            ]
        
        return c == 0

class UPIValidator:
    """UPI ID validator"""
    
    @staticmethod
    def validate(upi_id: str) -> bool:
        """Validate UPI ID format: user@bank"""
        if not upi_id:
            return False
        
        pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$'
        return bool(re.match(pattern, upi_id))

class TransactionValidator:
    """Transaction amount and limits validator"""
    
    @staticmethod
    def validate_amount(amount: float, min_amount: float = 1.0, max_amount: float = 1000000.0) -> bool:
        """Validate transaction amount within limits"""
        return min_amount <= amount <= max_amount
    
    @staticmethod
    def validate_account_number(account_number: str) -> bool:
        """Validate account number (9-18 digits)"""
        if not account_number:
            return False
        
        return account_number.isdigit() and 9 <= len(account_number) <= 18
    
    @staticmethod
    def validate_mobile_number(mobile: str) -> bool:
        """Validate Indian mobile number"""
        if not mobile:
            return False
        
        pattern = r'^[6-9]\d{9}$'
        return bool(re.match(pattern, mobile))

class GSTValidator:
    """GST number validator"""
    
    @staticmethod
    def validate(gst_number: str) -> bool:
        """Validate GST number format"""
        if not gst_number or len(gst_number) != 15:
            return False
        
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        return bool(re.match(pattern, gst_number.upper()))