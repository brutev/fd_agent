import 'dart:math';

class Validators {
  // Mobile number validation (Indian format)
  static String? validateMobileNumber(String? value) {
    if (value == null || value.isEmpty) {
      return 'Mobile number is required';
    }
    
    final cleanValue = value.replaceAll(RegExp(r'[^\d]'), '');
    
    if (cleanValue.length != 10) {
      return 'Mobile number must be 10 digits';
    }
    
    if (!RegExp(r'^[6-9]\d{9}$').hasMatch(cleanValue)) {
      return 'Invalid mobile number format';
    }
    
    return null;
  }
  
  // IFSC code validation
  static String? validateIFSC(String? value) {
    if (value == null || value.isEmpty) {
      return 'IFSC code is required';
    }
    
    final cleanValue = value.toUpperCase().trim();
    
    if (cleanValue.length != 11) {
      return 'IFSC code must be 11 characters';
    }
    
    if (!RegExp(r'^[A-Z]{4}0[A-Z0-9]{6}$').hasMatch(cleanValue)) {
      return 'Invalid IFSC code format';
    }
    
    return null;
  }
  
  // PAN card validation
  static String? validatePAN(String? value) {
    if (value == null || value.isEmpty) {
      return 'PAN number is required';
    }
    
    final cleanValue = value.toUpperCase().trim();
    
    if (cleanValue.length != 10) {
      return 'PAN number must be 10 characters';
    }
    
    if (!RegExp(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$').hasMatch(cleanValue)) {
      return 'Invalid PAN number format';
    }
    
    return null;
  }
  
  // Aadhaar validation with Verhoeff algorithm
  static String? validateAadhaar(String? value) {
    if (value == null || value.isEmpty) {
      return 'Aadhaar number is required';
    }
    
    final cleanValue = value.replaceAll(RegExp(r'[^\d]'), '');
    
    if (cleanValue.length != 12) {
      return 'Aadhaar number must be 12 digits';
    }
    
    if (!_verifyAadhaarChecksum(cleanValue)) {
      return 'Invalid Aadhaar number';
    }
    
    return null;
  }
  
  // Account number validation
  static String? validateAccountNumber(String? value) {
    if (value == null || value.isEmpty) {
      return 'Account number is required';
    }
    
    final cleanValue = value.replaceAll(RegExp(r'[^\d]'), '');
    
    if (cleanValue.length < 9 || cleanValue.length > 18) {
      return 'Account number must be 9-18 digits';
    }
    
    return null;
  }
  
  // UPI ID validation
  static String? validateUPIId(String? value) {
    if (value == null || value.isEmpty) {
      return 'UPI ID is required';
    }
    
    if (!RegExp(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$').hasMatch(value)) {
      return 'Invalid UPI ID format';
    }
    
    final validHandles = [
      'paytm', 'phonepe', 'gpay', 'amazonpay', 'mobikwik',
      'freecharge', 'airtel', 'jio', 'sbi', 'hdfc', 'icici',
      'axis', 'kotak', 'pnb', 'bob', 'canara', 'union'
    ];
    
    final handle = value.split('@')[1].toLowerCase();
    final isValidHandle = validHandles.any((validHandle) => handle.contains(validHandle));
    
    if (!isValidHandle) {
      return 'Invalid UPI handle';
    }
    
    return null;
  }
  
  // Amount validation
  static String? validateAmount(String? value, {double? minAmount, double? maxAmount}) {
    if (value == null || value.isEmpty) {
      return 'Amount is required';
    }
    
    final amount = double.tryParse(value);
    if (amount == null) {
      return 'Invalid amount format';
    }
    
    if (amount <= 0) {
      return 'Amount must be greater than zero';
    }
    
    if (minAmount != null && amount < minAmount) {
      return 'Amount must be at least ₹${minAmount.toStringAsFixed(2)}';
    }
    
    if (maxAmount != null && amount > maxAmount) {
      return 'Amount cannot exceed ₹${maxAmount.toStringAsFixed(2)}';
    }
    
    return null;
  }
  
  // NEFT amount validation
  static String? validateNEFTAmount(String? value) {
    return validateAmount(value, minAmount: 1.0, maxAmount: 1000000.0);
  }
  
  // UPI amount validation
  static String? validateUPIAmount(String? value) {
    return validateAmount(value, minAmount: 1.0, maxAmount: 100000.0);
  }
  
  // RTGS amount validation
  static String? validateRTGSAmount(String? value) {
    return validateAmount(value, minAmount: 200000.0, maxAmount: 10000000.0);
  }
  
  // IMPS amount validation
  static String? validateIMPSAmount(String? value) {
    return validateAmount(value, minAmount: 1.0, maxAmount: 500000.0);
  }
  
  // Email validation
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email is required';
    }
    
    if (!RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').hasMatch(value)) {
      return 'Invalid email format';
    }
    
    return null;
  }
  
  // Password validation
  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password is required';
    }
    
    if (value.length < 8) {
      return 'Password must be at least 8 characters';
    }
    
    if (!RegExp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]').hasMatch(value)) {
      return 'Password must contain uppercase, lowercase, number and special character';
    }
    
    return null;
  }
  
  // MPIN validation
  static String? validateMPIN(String? value) {
    if (value == null || value.isEmpty) {
      return 'MPIN is required';
    }
    
    if (value.length != 4) {
      return 'MPIN must be 4 digits';
    }
    
    if (!RegExp(r'^\d{4}$').hasMatch(value)) {
      return 'MPIN must contain only numbers';
    }
    
    // Check for sequential or repeated digits
    if (_hasSequentialDigits(value) || _hasRepeatedDigits(value)) {
      return 'MPIN cannot have sequential or repeated digits';
    }
    
    return null;
  }
  
  // OTP validation
  static String? validateOTP(String? value) {
    if (value == null || value.isEmpty) {
      return 'OTP is required';
    }
    
    if (value.length != 6) {
      return 'OTP must be 6 digits';
    }
    
    if (!RegExp(r'^\d{6}$').hasMatch(value)) {
      return 'OTP must contain only numbers';
    }
    
    return null;
  }
  
  // Transaction remarks validation
  static String? validateRemarks(String? value) {
    if (value != null && value.isNotEmpty) {
      if (value.length > 50) {
        return 'Remarks cannot exceed 50 characters';
      }
      
      if (!RegExp(r'^[a-zA-Z0-9\s.,\-_]+$').hasMatch(value)) {
        return 'Remarks contain invalid characters';
      }
    }
    
    return null;
  }
  
  // Name validation
  static String? validateName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Name is required';
    }
    
    if (value.length < 2) {
      return 'Name must be at least 2 characters';
    }
    
    if (value.length > 50) {
      return 'Name cannot exceed 50 characters';
    }
    
    if (!RegExp(r'^[a-zA-Z\s.]+$').hasMatch(value)) {
      return 'Name can only contain letters, spaces and dots';
    }
    
    return null;
  }
  
  // Required field validation
  static String? validateRequired(String? value, String fieldName) {
    if (value == null || value.trim().isEmpty) {
      return '$fieldName is required';
    }
    return null;
  }
  
  // Verhoeff algorithm for Aadhaar validation
  static bool _verifyAadhaarChecksum(String aadhaar) {
    final verhoeffTable = [
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
    ];
    
    final permutationTable = [
      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
      [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
      [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
      [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
      [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
      [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
      [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
      [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ];
    
    int c = 0;
    final reversedAadhaar = aadhaar.split('').reversed.toList();
    
    for (int i = 0; i < reversedAadhaar.length; i++) {
      final digit = int.parse(reversedAadhaar[i]);
      c = verhoeffTable[c][permutationTable[(i + 1) % 8][digit]];
    }
    
    return c == 0;
  }
  
  // Check for sequential digits in MPIN
  static bool _hasSequentialDigits(String mpin) {
    for (int i = 0; i < mpin.length - 1; i++) {
      final current = int.parse(mpin[i]);
      final next = int.parse(mpin[i + 1]);
      if ((next - current).abs() == 1) {
        return true;
      }
    }
    return false;
  }
  
  // Check for repeated digits in MPIN
  static bool _hasRepeatedDigits(String mpin) {
    final digits = mpin.split('');
    final uniqueDigits = digits.toSet();
    return uniqueDigits.length < digits.length;
  }
  
  // Mask Aadhaar number
  static String maskAadhaar(String aadhaar) {
    if (aadhaar.length != 12) return aadhaar;
    return 'XXXX XXXX ${aadhaar.substring(8)}';
  }
  
  // Mask account number
  static String maskAccountNumber(String accountNumber) {
    if (accountNumber.length < 4) return accountNumber;
    final visibleDigits = accountNumber.substring(accountNumber.length - 4);
    final maskedPart = 'X' * (accountNumber.length - 4);
    return '$maskedPart$visibleDigits';
  }
  
  // Format mobile number
  static String formatMobileNumber(String mobile) {
    final cleanMobile = mobile.replaceAll(RegExp(r'[^\d]'), '');
    if (cleanMobile.length == 10) {
      return '+91 ${cleanMobile.substring(0, 5)} ${cleanMobile.substring(5)}';
    }
    return mobile;
  }
  
  // Format amount with Indian currency format
  static String formatAmount(double amount) {
    final formatter = RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))');
    final amountStr = amount.toStringAsFixed(2);
    return '₹${amountStr.replaceAllMapped(formatter, (Match m) => '${m[1]},')}';
  }
}