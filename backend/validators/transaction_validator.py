import re
from datetime import datetime, time
from typing import Dict, Any

class TransactionValidator:
    """Transaction amount and limits validator"""
    
    # Transaction limits (in INR)
    LIMITS = {
        'NEFT': {'min': 1.0, 'max': 1000000.0},
        'RTGS': {'min': 200000.0, 'max': 10000000.0},
        'IMPS': {'min': 1.0, 'max': 500000.0},
        'UPI': {'min': 1.0, 'max': 100000.0}
    }
    
    # Operating hours
    OPERATING_HOURS = {
        'NEFT': {'start': time(8, 0), 'end': time(19, 0)},
        'RTGS': {'start': time(9, 0), 'end': time(16, 30)},
        'IMPS': {'start': time(0, 0), 'end': time(23, 59)},
        'UPI': {'start': time(0, 0), 'end': time(23, 59)}
    }
    
    @staticmethod
    def validate_amount(amount: float, transaction_type: str) -> Dict[str, Any]:
        """Validate transaction amount within limits"""
        if transaction_type not in TransactionValidator.LIMITS:
            return {'valid': False, 'error': 'Invalid transaction type'}
        
        limits = TransactionValidator.LIMITS[transaction_type]
        
        if amount < limits['min']:
            return {
                'valid': False, 
                'error': f'Amount below minimum limit of ₹{limits["min"]}'
            }
        
        if amount > limits['max']:
            return {
                'valid': False, 
                'error': f'Amount exceeds maximum limit of ₹{limits["max"]}'
            }
        
        return {'valid': True, 'error': None}
    
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
    
    @staticmethod
    def validate_operating_hours(transaction_type: str, transaction_time: datetime = None) -> Dict[str, Any]:
        """Validate if transaction is within operating hours"""
        if transaction_time is None:
            transaction_time = datetime.now()
        
        if transaction_type not in TransactionValidator.OPERATING_HOURS:
            return {'valid': False, 'error': 'Invalid transaction type'}
        
        hours = TransactionValidator.OPERATING_HOURS[transaction_type]
        current_time = transaction_time.time()
        
        # Check if current time is within operating hours
        if hours['start'] <= current_time <= hours['end']:
            return {'valid': True, 'error': None}
        
        return {
            'valid': False,
            'error': f'{transaction_type} transactions are available from {hours["start"]} to {hours["end"]}'
        }
    
    @staticmethod
    def validate_transaction_reference(reference: str) -> bool:
        """Validate transaction reference number format"""
        if not reference:
            return False
        
        # UTR format: YYMMDDHHMMSSNNNNN (17 digits)
        pattern = r'^\d{17}$'
        return bool(re.match(pattern, reference))
    
    @staticmethod
    def validate_remarks(remarks: str) -> bool:
        """Validate transaction remarks"""
        if not remarks:
            return True  # Remarks are optional
        
        # Max 50 characters, alphanumeric and basic punctuation
        if len(remarks) > 50:
            return False
        
        pattern = r'^[a-zA-Z0-9\s.,\-_]+$'
        return bool(re.match(pattern, remarks))