import re

class UPIValidator:
    """UPI ID validator"""
    
    VALID_UPI_HANDLES = [
        'paytm', 'phonepe', 'gpay', 'amazonpay', 'mobikwik',
        'freecharge', 'airtel', 'jio', 'sbi', 'hdfc', 'icici',
        'axis', 'kotak', 'pnb', 'bob', 'canara', 'union',
        'indian', 'federal', 'yes', 'idfc', 'rbl'
    ]
    
    @staticmethod
    def validate(upi_id: str) -> bool:
        """Validate UPI ID format: user@bank"""
        if not upi_id:
            return False
        
        pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$'
        if not re.match(pattern, upi_id):
            return False
        
        # Additional validation for common UPI handles
        handle = upi_id.split('@')[1].lower()
        return any(valid_handle in handle for valid_handle in UPIValidator.VALID_UPI_HANDLES)
    
    @staticmethod
    def get_provider(upi_id: str) -> str:
        """Get UPI provider from UPI ID"""
        if not UPIValidator.validate(upi_id):
            return "Unknown"
        
        handle = upi_id.split('@')[1].lower()
        
        provider_map = {
            'paytm': 'Paytm',
            'phonepe': 'PhonePe',
            'gpay': 'Google Pay',
            'amazonpay': 'Amazon Pay',
            'sbi': 'State Bank of India',
            'hdfc': 'HDFC Bank',
            'icici': 'ICICI Bank',
            'axis': 'Axis Bank',
            'kotak': 'Kotak Mahindra Bank'
        }
        
        for key, value in provider_map.items():
            if key in handle:
                return value
        
        return "Other Bank"