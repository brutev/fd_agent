import 'package:flutter_test/flutter_test.dart';
import 'package:fd_agent_mobile/shared/utils/validators.dart';

void main() {
  group('Mobile Number Validation', () {
    test('should return null for valid mobile numbers', () {
      final validNumbers = [
        '9876543210',
        '8765432109',
        '7654321098',
        '6543210987',
        '+91 9876543210',
        '91 9876543210',
        '9876-543-210',
        '98765 43210'
      ];
      
      for (final number in validNumbers) {
        expect(Validators.validateMobileNumber(number), isNull);
      }
    });
    
    test('should return error for invalid mobile numbers', () {
      final invalidNumbers = [
        '1234567890', // Doesn't start with 6-9
        '98765432101', // Too long
        '987654321', // Too short
        '9876543abc', // Contains letters
        '', // Empty
        null, // Null
        '5876543210', // Starts with 5
        '0876543210', // Starts with 0
      ];
      
      for (final number in invalidNumbers) {
        expect(Validators.validateMobileNumber(number), isNotNull);
      }
    });
  });
  
  group('IFSC Code Validation', () {
    test('should return null for valid IFSC codes', () {
      final validCodes = [
        'SBIN0000001',
        'HDFC0000001',
        'ICIC0000001',
        'AXIS0000001',
        'PUNB0000001',
        'sbin0000001', // Should handle lowercase
      ];
      
      for (final code in validCodes) {
        expect(Validators.validateIFSC(code), isNull);
      }
    });
    
    test('should return error for invalid IFSC codes', () {
      final invalidCodes = [
        'SBIN000001', // Too short
        'SBIN00000001', // Too long
        'SBIN1000001', // Invalid 5th character
        '1BIN0000001', // Number in bank code
        '', // Empty
        null, // Null
        'ABCD', // Too short
      ];
      
      for (final code in invalidCodes) {
        expect(Validators.validateIFSC(code), isNotNull);
      }
    });
  });
  
  group('PAN Validation', () {
    test('should return null for valid PAN numbers', () {
      final validPANs = [
        'ABCDE1234F',
        'PQRST5678G',
        'LMNOP9012H',
        'abcde1234f', // Should handle lowercase
      ];
      
      for (final pan in validPANs) {
        expect(Validators.validatePAN(pan), isNull);
      }
    });
    
    test('should return error for invalid PAN numbers', () {
      final invalidPANs = [
        'ABCDE1234', // Too short
        'ABCDE12345F', // Too long
        '12345ABCDF', // Numbers first
        'ABCDE12F4F', // Letter in number position
        '', // Empty
        null, // Null
      ];
      
      for (final pan in invalidPANs) {
        expect(Validators.validatePAN(pan), isNotNull);
      }
    });
  });
  
  group('Aadhaar Validation', () {
    test('should return null for valid format Aadhaar numbers', () {
      // Note: These are test numbers, not real Aadhaar numbers
      final validAadhaars = [
        '123456789012',
        '1234 5678 9012',
        '1234-5678-9012',
      ];
      
      for (final aadhaar in validAadhaars) {
        // Test format validation (Verhoeff algorithm may fail for test numbers)
        final result = Validators.validateAadhaar(aadhaar);
        // Should either be null (valid) or contain "Invalid Aadhaar number" (checksum failed)
        expect(result == null || result!.contains('Invalid Aadhaar number'), isTrue);
      }
    });
    
    test('should return error for invalid Aadhaar format', () {
      final invalidAadhaars = [
        '12345678901', // Too short
        '1234567890123', // Too long
        '12345678901a', // Contains letter
        '', // Empty
        null, // Null
        '000000000000', // All zeros
      ];
      
      for (final aadhaar in invalidAadhaars) {
        final result = Validators.validateAadhaar(aadhaar);
        expect(result, isNotNull);
        expect(result!.contains('12 digits') || result.contains('required'), isTrue);
      }
    });
  });
  
  group('Account Number Validation', () {
    test('should return null for valid account numbers', () {
      final validAccounts = [
        '123456789', // 9 digits
        '12345678901234567890', // 18 digits (with formatting)
        '1234567890123456', // 16 digits
        '1234-5678-9012-3456', // With dashes
        '1234 5678 9012 3456', // With spaces
      ];
      
      for (final account in validAccounts) {
        expect(Validators.validateAccountNumber(account), isNull);
      }
    });
    
    test('should return error for invalid account numbers', () {
      final invalidAccounts = [
        '12345678', // Too short
        '123456789012345678901', // Too long
        '12345678a', // Contains letter
        '', // Empty
        null, // Null
      ];
      
      for (final account in invalidAccounts) {
        expect(Validators.validateAccountNumber(account), isNotNull);
      }
    });
  });
  
  group('UPI ID Validation', () {
    test('should return null for valid UPI IDs', () {
      final validUPIs = [
        'user@paytm',
        'test@phonepe',
        'customer@gpay',
        'user123@sbi',
        'test.user@hdfc',
        'user_name@icici',
        'user-123@axis',
      ];
      
      for (final upi in validUPIs) {
        expect(Validators.validateUPIId(upi), isNull);
      }
    });
    
    test('should return error for invalid UPI IDs', () {
      final invalidUPIs = [
        'user', // No @ symbol
        '@paytm', // No user part
        'user@', // No handle part
        '', // Empty
        null, // Null
        'user@invalid', // Invalid handle
        'user@@paytm', // Double @
        'user@pay tm', // Space in handle
      ];
      
      for (final upi in invalidUPIs) {
        expect(Validators.validateUPIId(upi), isNotNull);
      }
    });
  });
  
  group('Amount Validation', () {
    test('should return null for valid amounts', () {
      final validAmounts = [
        '100',
        '1000.50',
        '50000',
        '999999.99',
      ];
      
      for (final amount in validAmounts) {
        expect(Validators.validateAmount(amount), isNull);
      }
    });
    
    test('should return error for invalid amounts', () {
      final invalidAmounts = [
        '0', // Zero
        '-100', // Negative
        'abc', // Not a number
        '', // Empty
        null, // Null
        '100.123', // Too many decimal places (handled by double.parse)
      ];
      
      for (final amount in invalidAmounts) {
        expect(Validators.validateAmount(amount), isNotNull);
      }
    });
    
    test('should validate amount limits', () {
      // Test minimum limit
      expect(Validators.validateAmount('50', minAmount: 100), isNotNull);
      expect(Validators.validateAmount('150', minAmount: 100), isNull);
      
      // Test maximum limit
      expect(Validators.validateAmount('150000', maxAmount: 100000), isNotNull);
      expect(Validators.validateAmount('50000', maxAmount: 100000), isNull);
    });
  });
  
  group('Transaction Amount Validation', () {
    test('should validate NEFT amounts correctly', () {
      expect(Validators.validateNEFTAmount('100'), isNull);
      expect(Validators.validateNEFTAmount('500000'), isNull);
      expect(Validators.validateNEFTAmount('0.5'), isNotNull); // Below minimum
      expect(Validators.validateNEFTAmount('2000000'), isNotNull); // Above maximum
    });
    
    test('should validate UPI amounts correctly', () {
      expect(Validators.validateUPIAmount('50'), isNull);
      expect(Validators.validateUPIAmount('50000'), isNull);
      expect(Validators.validateUPIAmount('0.5'), isNotNull); // Below minimum
      expect(Validators.validateUPIAmount('150000'), isNotNull); // Above maximum
    });
    
    test('should validate RTGS amounts correctly', () {
      expect(Validators.validateRTGSAmount('300000'), isNull);
      expect(Validators.validateRTGSAmount('5000000'), isNull);
      expect(Validators.validateRTGSAmount('100000'), isNotNull); // Below minimum
      expect(Validators.validateRTGSAmount('15000000'), isNotNull); // Above maximum
    });
  });
  
  group('Email Validation', () {
    test('should return null for valid emails', () {
      final validEmails = [
        'test@example.com',
        'user.name@domain.co.in',
        'user+tag@example.org',
        'user123@test-domain.com',
      ];
      
      for (final email in validEmails) {
        expect(Validators.validateEmail(email), isNull);
      }
    });
    
    test('should return error for invalid emails', () {
      final invalidEmails = [
        'invalid-email',
        '@domain.com',
        'user@',
        'user@domain',
        '',
        null,
      ];
      
      for (final email in invalidEmails) {
        expect(Validators.validateEmail(email), isNotNull);
      }
    });
  });
  
  group('Password Validation', () {
    test('should return null for valid passwords', () {
      final validPasswords = [
        'Password123!',
        'MySecure@Pass1',
        'Strong#Pass99',
      ];
      
      for (final password in validPasswords) {
        expect(Validators.validatePassword(password), isNull);
      }
    });
    
    test('should return error for invalid passwords', () {
      final invalidPasswords = [
        'short', // Too short
        'password', // No uppercase, number, special char
        'PASSWORD', // No lowercase, number, special char
        '12345678', // No letters, special char
        'Password1', // No special char
        '',
        null,
      ];
      
      for (final password in invalidPasswords) {
        expect(Validators.validatePassword(password), isNotNull);
      }
    });
  });
  
  group('MPIN Validation', () {
    test('should return null for valid MPINs', () {
      final validMPINs = [
        '1357',
        '2468',
        '9876',
        '1029',
      ];
      
      for (final mpin in validMPINs) {
        expect(Validators.validateMPIN(mpin), isNull);
      }
    });
    
    test('should return error for invalid MPINs', () {
      final invalidMPINs = [
        '123', // Too short
        '12345', // Too long
        '123a', // Contains letter
        '1234', // Sequential digits
        '1111', // Repeated digits
        '2345', // Sequential digits
        '',
        null,
      ];
      
      for (final mpin in invalidMPINs) {
        expect(Validators.validateMPIN(mpin), isNotNull);
      }
    });
  });
  
  group('OTP Validation', () {
    test('should return null for valid OTPs', () {
      final validOTPs = [
        '123456',
        '987654',
        '000000',
        '999999',
      ];
      
      for (final otp in validOTPs) {
        expect(Validators.validateOTP(otp), isNull);
      }
    });
    
    test('should return error for invalid OTPs', () {
      final invalidOTPs = [
        '12345', // Too short
        '1234567', // Too long
        '12345a', // Contains letter
        '',
        null,
      ];
      
      for (final otp in invalidOTPs) {
        expect(Validators.validateOTP(otp), isNotNull);
      }
    });
  });
  
  group('Utility Functions', () {
    test('should mask Aadhaar correctly', () {
      expect(Validators.maskAadhaar('123456789012'), equals('XXXX XXXX 9012'));
      expect(Validators.maskAadhaar('invalid'), equals('invalid'));
    });
    
    test('should mask account number correctly', () {
      expect(Validators.maskAccountNumber('1234567890123456'), equals('XXXXXXXXXXXX3456'));
      expect(Validators.maskAccountNumber('123'), equals('123'));
    });
    
    test('should format mobile number correctly', () {
      expect(Validators.formatMobileNumber('9876543210'), equals('+91 98765 43210'));
      expect(Validators.formatMobileNumber('invalid'), equals('invalid'));
    });
    
    test('should format amount correctly', () {
      expect(Validators.formatAmount(1000), equals('₹1,000.00'));
      expect(Validators.formatAmount(100000), equals('₹1,00,000.00'));
      expect(Validators.formatAmount(1000000), equals('₹10,00,000.00'));
    });
  });
  
  group('Edge Cases', () {
    test('should handle whitespace in inputs', () {
      expect(Validators.validateMobileNumber('  9876543210  '), isNull);
      expect(Validators.validateIFSC('  SBIN0000001  '), isNull);
      expect(Validators.validatePAN('  ABCDE1234F  '), isNull);
    });
    
    test('should handle case sensitivity', () {
      expect(Validators.validateIFSC('sbin0000001'), isNull);
      expect(Validators.validatePAN('abcde1234f'), isNull);
    });
    
    test('should validate required fields', () {
      expect(Validators.validateRequired('value', 'Field'), isNull);
      expect(Validators.validateRequired('', 'Field'), contains('Field is required'));
      expect(Validators.validateRequired(null, 'Field'), contains('Field is required'));
      expect(Validators.validateRequired('   ', 'Field'), contains('Field is required'));
    });
    
    test('should validate names correctly', () {
      expect(Validators.validateName('John Doe'), isNull);
      expect(Validators.validateName('Dr. Smith'), isNull);
      expect(Validators.validateName('A'), isNotNull); // Too short
      expect(Validators.validateName('A' * 51), isNotNull); // Too long
      expect(Validators.validateName('John123'), isNotNull); // Contains numbers
      expect(Validators.validateName(''), isNotNull); // Empty
    });
    
    test('should validate remarks correctly', () {
      expect(Validators.validateRemarks('Payment for services'), isNull);
      expect(Validators.validateRemarks(''), isNull); // Empty is valid
      expect(Validators.validateRemarks(null), isNull); // Null is valid
      expect(Validators.validateRemarks('A' * 51), isNotNull); // Too long
      expect(Validators.validateRemarks('Payment@#\$'), isNotNull); // Invalid chars
    });
  });
}