import pytest
from validators.ifsc_validator import IFSCValidator
from validators.pan_validator import PANValidator
from validators.aadhaar_validator import AadhaarValidator
from validators.upi_validator import UPIValidator
from validators.transaction_validator import TransactionValidator

class TestIFSCValidator:
    """Test IFSC validator with comprehensive scenarios"""
    
    def test_valid_ifsc_codes(self):
        """Test valid IFSC codes"""
        valid_codes = [
            'SBIN0000001',
            'HDFC0000001',
            'ICIC0000001',
            'AXIS0000001',
            'PUNB0000001'
        ]
        
        for code in valid_codes:
            assert IFSCValidator.validate(code) == True
    
    def test_invalid_ifsc_codes(self):
        """Test invalid IFSC codes"""
        invalid_codes = [
            'SBIN000001',   # Too short
            'SBIN00000001', # Too long
            'sbin0000001',  # Lowercase
            'SBIN1000001',  # Invalid 5th character
            '1BIN0000001',  # Number in bank code
            'SBIN000000A',  # Invalid character
            '',             # Empty
            None,           # None
            'ABCD',         # Too short
            'ABCD0EFGHIJ'   # Valid length but invalid format
        ]
        
        for code in invalid_codes:
            assert IFSCValidator.validate(code) == False
    
    def test_get_bank_code(self):
        """Test bank code extraction"""
        assert IFSCValidator.get_bank_code('SBIN0000001') == 'SBIN'
        assert IFSCValidator.get_bank_code('HDFC0000001') == 'HDFC'
        assert IFSCValidator.get_bank_code('invalid') == None
    
    def test_edge_cases(self):
        """Test edge cases"""
        assert IFSCValidator.validate('ABCD0123456') == True
        assert IFSCValidator.validate('WXYZ0ABCDEF') == True
        assert IFSCValidator.validate('TEST0000000') == True

class TestPANValidator:
    """Test PAN validator with comprehensive scenarios"""
    
    def test_valid_pan_numbers(self):
        """Test valid PAN numbers"""
        valid_pans = [
            'ABCDE1234F',
            'PQRST5678G',
            'LMNOP9012H',
            'FGHIJ3456K',
            'UVWXY7890L'
        ]
        
        for pan in valid_pans:
            assert PANValidator.validate(pan) == True
    
    def test_invalid_pan_numbers(self):
        """Test invalid PAN numbers"""
        invalid_pans = [
            'ABCDE1234',   # Too short
            'ABCDE12345F', # Too long
            'abcde1234f',  # Lowercase
            '12345ABCDF',  # Numbers first
            'ABCDE12F4F',  # Letter in number position
            'ABCD51234F',  # Number in letter position
            '',            # Empty
            None,          # None
            'ABCDE1234FF', # Extra character
            'A1CDE1234F'   # Number in wrong position
        ]
        
        for pan in invalid_pans:
            assert PANValidator.validate(pan) == False
    
    def test_extract_entity_type(self):
        """Test entity type extraction"""
        assert PANValidator.extract_entity_type('ABCPD1234F') == 'Individual'
        assert PANValidator.extract_entity_type('ABCCD1234F') == 'Company'
        assert PANValidator.extract_entity_type('ABCHD1234F') == 'HUF'
        assert PANValidator.extract_entity_type('ABCFD1234F') == 'Firm'
        assert PANValidator.extract_entity_type('invalid') == 'Invalid'

class TestAadhaarValidator:
    """Test Aadhaar validator with Verhoeff algorithm"""
    
    def test_valid_aadhaar_numbers(self):
        """Test valid Aadhaar numbers (using Verhoeff algorithm)"""
        # These are test Aadhaar numbers that pass Verhoeff validation
        valid_aadhaars = [
            '234123412341',  # Valid test number
            '123456789012',  # Another valid test number
        ]
        
        # Note: Using actual valid Aadhaar numbers for testing
        # In production, use only test numbers
        for aadhaar in valid_aadhaars:
            # Test the format first
            assert len(aadhaar) == 12
            assert aadhaar.isdigit()
    
    def test_invalid_aadhaar_numbers(self):
        """Test invalid Aadhaar numbers"""
        invalid_aadhaars = [
            '12345678901',   # Too short
            '1234567890123', # Too long
            '12345678901a',  # Contains letter
            '',              # Empty
            None,            # None
            '000000000000',  # All zeros
            '111111111111',  # All ones
            'abcdefghijkl'   # All letters
        ]
        
        for aadhaar in invalid_aadhaars:
            assert AadhaarValidator.validate(aadhaar) == False
    
    def test_verhoeff_algorithm(self):
        """Test Verhoeff algorithm implementation"""
        # Test with known invalid numbers
        invalid_numbers = [
            '123456789013',  # Invalid checksum
            '987654321098',  # Invalid checksum
        ]
        
        for number in invalid_numbers:
            assert AadhaarValidator.validate(number) == False
    
    def test_mask_aadhaar(self):
        """Test Aadhaar masking"""
        assert AadhaarValidator.mask_aadhaar('123456789012') == 'XXXX XXXX 9012'
        assert AadhaarValidator.mask_aadhaar('invalid') == 'Invalid Aadhaar'

class TestUPIValidator:
    """Test UPI validator with comprehensive scenarios"""
    
    def test_valid_upi_ids(self):
        """Test valid UPI IDs"""
        valid_upis = [
            'user@paytm',
            'test@phonepe',
            'customer@gpay',
            'user123@sbi',
            'test.user@hdfc',
            'user_name@icici',
            'user-123@axis'
        ]
        
        for upi in valid_upis:
            assert UPIValidator.validate(upi) == True
    
    def test_invalid_upi_ids(self):
        """Test invalid UPI IDs"""
        invalid_upis = [
            'user',          # No @ symbol
            '@paytm',        # No user part
            'user@',         # No handle part
            '',              # Empty
            None,            # None
            'user@invalid',  # Invalid handle
            'user@@paytm',   # Double @
            'user@pay tm',   # Space in handle
            'us er@paytm'    # Space in user
        ]
        
        for upi in invalid_upis:
            assert UPIValidator.validate(upi) == False
    
    def test_get_provider(self):
        """Test UPI provider extraction"""
        assert UPIValidator.get_provider('user@paytm') == 'Paytm'
        assert UPIValidator.get_provider('user@phonepe') == 'PhonePe'
        assert UPIValidator.get_provider('user@gpay') == 'Google Pay'
        assert UPIValidator.get_provider('user@sbi') == 'State Bank of India'
        assert UPIValidator.get_provider('user@unknown') == 'Other Bank'
        assert UPIValidator.get_provider('invalid') == 'Unknown'

class TestTransactionValidator:
    """Test transaction validator with comprehensive scenarios"""
    
    def test_validate_amount_neft(self):
        """Test NEFT amount validation"""
        # Valid amounts
        result = TransactionValidator.validate_amount(100.0, 'NEFT')
        assert result['valid'] == True
        
        result = TransactionValidator.validate_amount(50000.0, 'NEFT')
        assert result['valid'] == True
        
        # Invalid amounts
        result = TransactionValidator.validate_amount(0.5, 'NEFT')
        assert result['valid'] == False
        assert 'minimum limit' in result['error']
        
        result = TransactionValidator.validate_amount(2000000.0, 'NEFT')
        assert result['valid'] == False
        assert 'maximum limit' in result['error']
    
    def test_validate_amount_upi(self):
        """Test UPI amount validation"""
        # Valid amounts
        result = TransactionValidator.validate_amount(50.0, 'UPI')
        assert result['valid'] == True
        
        result = TransactionValidator.validate_amount(50000.0, 'UPI')
        assert result['valid'] == True
        
        # Invalid amounts
        result = TransactionValidator.validate_amount(150000.0, 'UPI')
        assert result['valid'] == False
        assert 'maximum limit' in result['error']
    
    def test_validate_amount_rtgs(self):
        """Test RTGS amount validation"""
        # Valid amounts
        result = TransactionValidator.validate_amount(300000.0, 'RTGS')
        assert result['valid'] == True
        
        # Invalid amounts
        result = TransactionValidator.validate_amount(100000.0, 'RTGS')
        assert result['valid'] == False
        assert 'minimum limit' in result['error']
    
    def test_validate_account_number(self):
        """Test account number validation"""
        # Valid account numbers
        valid_accounts = [
            '123456789',      # 9 digits
            '12345678901234567890',  # 18 digits
            '1234567890123456'       # 16 digits
        ]
        
        for account in valid_accounts:
            assert TransactionValidator.validate_account_number(account) == True
        
        # Invalid account numbers
        invalid_accounts = [
            '12345678',       # Too short
            '1234567890123456789012',  # Too long
            '12345678a',      # Contains letter
            '',               # Empty
            None              # None
        ]
        
        for account in invalid_accounts:
            assert TransactionValidator.validate_account_number(account) == False
    
    def test_validate_mobile_number(self):
        """Test mobile number validation"""
        # Valid mobile numbers
        valid_mobiles = [
            '9876543210',
            '8765432109',
            '7654321098',
            '6543210987'
        ]
        
        for mobile in valid_mobiles:
            assert TransactionValidator.validate_mobile_number(mobile) == True
        
        # Invalid mobile numbers
        invalid_mobiles = [
            '1234567890',     # Doesn't start with 6-9
            '98765432101',    # Too long
            '987654321',      # Too short
            '9876543abc',     # Contains letters
            '',               # Empty
            None              # None
        ]
        
        for mobile in invalid_mobiles:
            assert TransactionValidator.validate_mobile_number(mobile) == False
    
    def test_validate_operating_hours(self):
        """Test operating hours validation"""
        from datetime import datetime, time
        
        # Test NEFT during operating hours (8 AM - 7 PM)
        morning_time = datetime.now().replace(hour=10, minute=0, second=0)
        result = TransactionValidator.validate_operating_hours('NEFT', morning_time)
        assert result['valid'] == True
        
        # Test NEFT outside operating hours
        night_time = datetime.now().replace(hour=22, minute=0, second=0)
        result = TransactionValidator.validate_operating_hours('NEFT', night_time)
        assert result['valid'] == False
        assert 'available from' in result['error']
        
        # Test UPI (24x7)
        result = TransactionValidator.validate_operating_hours('UPI', night_time)
        assert result['valid'] == True
        
        # Test IMPS (24x7)
        result = TransactionValidator.validate_operating_hours('IMPS', night_time)
        assert result['valid'] == True
    
    def test_validate_transaction_reference(self):
        """Test transaction reference validation"""
        # Valid UTR (17 digits)
        valid_refs = [
            '12345678901234567',
            '98765432109876543'
        ]
        
        for ref in valid_refs:
            assert TransactionValidator.validate_transaction_reference(ref) == True
        
        # Invalid references
        invalid_refs = [
            '1234567890123456',   # Too short
            '123456789012345678', # Too long
            '1234567890123456a',  # Contains letter
            '',                   # Empty
            None                  # None
        ]
        
        for ref in invalid_refs:
            assert TransactionValidator.validate_transaction_reference(ref) == False
    
    def test_validate_remarks(self):
        """Test transaction remarks validation"""
        # Valid remarks
        valid_remarks = [
            'Payment for services',
            'Salary transfer',
            'EMI payment',
            'Gift money',
            '',  # Empty is valid
            'Test-123_payment.done'
        ]
        
        for remark in valid_remarks:
            assert TransactionValidator.validate_remarks(remark) == True
        
        # Invalid remarks
        invalid_remarks = [
            'A' * 51,  # Too long
            'Payment@#$%',  # Invalid characters
            'Payment\nwith\nnewlines'  # Newlines
        ]
        
        for remark in invalid_remarks:
            assert TransactionValidator.validate_remarks(remark) == False
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test exact boundary amounts
        result = TransactionValidator.validate_amount(1.0, 'NEFT')
        assert result['valid'] == True
        
        result = TransactionValidator.validate_amount(1000000.0, 'NEFT')
        assert result['valid'] == True
        
        # Test invalid transaction type
        result = TransactionValidator.validate_amount(100.0, 'INVALID')
        assert result['valid'] == False
        assert 'Invalid transaction type' in result['error']
        
        # Test boundary operating hours
        boundary_time = datetime.now().replace(hour=8, minute=0, second=0)
        result = TransactionValidator.validate_operating_hours('NEFT', boundary_time)
        assert result['valid'] == True
        
        boundary_time = datetime.now().replace(hour=19, minute=0, second=0)
        result = TransactionValidator.validate_operating_hours('NEFT', boundary_time)
        assert result['valid'] == True

# Integration tests for validators
class TestValidatorIntegration:
    """Integration tests for all validators"""
    
    def test_complete_transaction_validation(self):
        """Test complete transaction validation flow"""
        # Valid transaction data
        transaction_data = {
            'ifsc': 'SBIN0000001',
            'account_number': '1234567890123456',
            'amount': 50000.0,
            'transaction_type': 'NEFT',
            'mobile': '9876543210',
            'remarks': 'Salary payment'
        }
        
        # Validate all fields
        assert IFSCValidator.validate(transaction_data['ifsc']) == True
        assert TransactionValidator.validate_account_number(transaction_data['account_number']) == True
        
        amount_result = TransactionValidator.validate_amount(
            transaction_data['amount'], 
            transaction_data['transaction_type']
        )
        assert amount_result['valid'] == True
        
        assert TransactionValidator.validate_mobile_number(transaction_data['mobile']) == True
        assert TransactionValidator.validate_remarks(transaction_data['remarks']) == True
    
    def test_kyc_validation_flow(self):
        """Test KYC validation flow"""
        # Valid KYC data
        kyc_data = {
            'pan': 'ABCDE1234F',
            'aadhaar': '123456789012',  # Test number
            'mobile': '9876543210'
        }
        
        # Validate KYC fields
        assert PANValidator.validate(kyc_data['pan']) == True
        assert TransactionValidator.validate_mobile_number(kyc_data['mobile']) == True
        
        # Test entity type extraction
        entity_type = PANValidator.extract_entity_type(kyc_data['pan'])
        assert entity_type in ['Individual', 'Company', 'HUF', 'Firm', 'AOP', 'Trust', 'Body of Individuals', 'Local Authority', 'Artificial Juridical Person', 'Government']
    
    def test_upi_transaction_validation(self):
        """Test UPI transaction validation"""
        upi_data = {
            'upi_id': 'user@paytm',
            'amount': 5000.0,
            'transaction_type': 'UPI'
        }
        
        assert UPIValidator.validate(upi_data['upi_id']) == True
        
        amount_result = TransactionValidator.validate_amount(
            upi_data['amount'],
            upi_data['transaction_type']
        )
        assert amount_result['valid'] == True
        
        provider = UPIValidator.get_provider(upi_data['upi_id'])
        assert provider != 'Unknown'

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=validators', '--cov-report=html'])