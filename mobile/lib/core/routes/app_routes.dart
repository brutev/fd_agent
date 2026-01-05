class AppRoutes {
  // Splash and onboarding
  static const String splash = '/';
  static const String onboarding = '/onboarding';
  
  // Authentication
  static const String login = '/login';
  static const String register = '/register';
  static const String forgotPassword = '/forgot-password';
  static const String resetPassword = '/reset-password';
  static const String verifyOtp = '/verify-otp';
  
  // Main app
  static const String home = '/home';
  static const String dashboard = '/dashboard';
  
  // Accounts
  static const String accounts = '/accounts';
  static const String accountDetails = '/account-details';
  static const String createAccount = '/create-account';
  
  // Transactions
  static const String transactions = '/transactions';
  static const String transactionDetails = '/transaction-details';
  static const String neftTransfer = '/neft-transfer';
  static const String impsTransfer = '/imps-transfer';
  static const String rtgsTransfer = '/rtgs-transfer';
  static const String upiTransfer = '/upi-transfer';
  
  // KYC
  static const String kyc = '/kyc';
  static const String kycVerification = '/kyc-verification';
  static const String aadhaarVerification = '/aadhaar-verification';
  static const String panVerification = '/pan-verification';
  
  // Loans
  static const String loans = '/loans';
  static const String loanApplication = '/loan-application';
  static const String loanDetails = '/loan-details';
  
  // Profile and settings
  static const String profile = '/profile';
  static const String settings = '/settings';
  static const String changePassword = '/change-password';
  static const String notifications = '/notifications';
  
  // Support
  static const String help = '/help';
  static const String contactSupport = '/contact-support';
}
