# Sample Change Request Implementations

This document demonstrates how the FD Agent System handles various types of change requests with complete implementation suggestions.

## CR-001: UPI AutoPay Mandate Feature

**Description**: Add UPI AutoPay mandate feature for recurring payments with merchant registration and automatic debit functionality.

**Agent Analysis**:
- Pattern: `upi_autopay`
- Confidence: 0.85
- Keywords: ['upi', 'autopay', 'mandate', 'recurring', 'payments']
- Priority: High
- Complexity: High

**Implementation Suggestions**:

### Flutter Changes:
```dart
// New Screen: UPI AutoPay Setup
class UPIAutopaySetupPage extends StatefulWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Setup UPI AutoPay')),
      body: Form(
        child: Column(
          children: [
            // Merchant selection
            DropdownButtonFormField<Merchant>(
              decoration: InputDecoration(labelText: 'Select Merchant'),
              items: merchants.map((merchant) => 
                DropdownMenuItem(value: merchant, child: Text(merchant.name))
              ).toList(),
              onChanged: (merchant) => selectedMerchant = merchant,
            ),
            
            // Amount limit
            TextFormField(
              decoration: InputDecoration(labelText: 'Maximum Amount per Transaction'),
              validator: (value) => Validators.validateUPIAmount(value),
              keyboardType: TextInputType.number,
            ),
            
            // Frequency selection
            DropdownButtonFormField<String>(
              decoration: InputDecoration(labelText: 'Frequency'),
              items: ['Daily', 'Weekly', 'Monthly'].map((freq) =>
                DropdownMenuItem(value: freq, child: Text(freq))
              ).toList(),
            ),
            
            // Start and end date
            DateRangeSelector(),
            
            // Setup button
            ElevatedButton(
              onPressed: () => _setupMandate(),
              child: Text('Setup AutoPay'),
            ),
          ],
        ),
      ),
    );
  }
  
  void _setupMandate() async {
    final response = await dio.post('/api/v1/upi/mandate/create', data: {
      'merchant_id': selectedMerchant.id,
      'amount_limit': amountController.text,
      'frequency': selectedFrequency,
      'start_date': startDate.toIso8601String(),
      'end_date': endDate.toIso8601String(),
    });
  }
}

// New Screen: Mandate Management
class MandateManagementPage extends StatefulWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Manage AutoPay')),
      body: BlocBuilder<MandateBloc, MandateState>(
        builder: (context, state) {
          if (state is MandatesLoaded) {
            return ListView.builder(
              itemCount: state.mandates.length,
              itemBuilder: (context, index) {
                final mandate = state.mandates[index];
                return MandateCard(
                  mandate: mandate,
                  onPause: () => _pauseMandate(mandate.id),
                  onModify: () => _modifyMandate(mandate.id),
                  onCancel: () => _cancelMandate(mandate.id),
                );
              },
            );
          }
          return CircularProgressIndicator();
        },
      ),
    );
  }
}
```

### Python Changes:
```python
# New API Endpoints
@router.post("/api/v1/upi/mandate/create")
async def create_upi_mandate(
    mandate_request: UPIMandateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate mandate parameters
    if mandate_request.amount_limit > 100000:
        raise HTTPException(status_code=400, detail="Amount limit exceeds UPI AutoPay maximum")
    
    # Validate merchant
    merchant = MerchantService.get_merchant(db, mandate_request.merchant_id)
    if not merchant or not merchant.autopay_enabled:
        raise HTTPException(status_code=400, detail="Merchant not eligible for AutoPay")
    
    # Create mandate with NPCI
    npci_response = NPCIService.create_mandate(
        user_id=current_user.id,
        merchant_id=mandate_request.merchant_id,
        amount_limit=mandate_request.amount_limit,
        frequency=mandate_request.frequency,
        start_date=mandate_request.start_date,
        end_date=mandate_request.end_date
    )
    
    # Store mandate in database
    mandate = UPIMandateService.create_mandate(
        db=db,
        user_id=current_user.id,
        merchant_id=mandate_request.merchant_id,
        npci_mandate_id=npci_response.mandate_id,
        amount_limit=mandate_request.amount_limit,
        frequency=mandate_request.frequency,
        start_date=mandate_request.start_date,
        end_date=mandate_request.end_date,
        status=MandateStatus.ACTIVE
    )
    
    return UPIMandateResponse(
        mandate_id=mandate.id,
        npci_mandate_id=npci_response.mandate_id,
        status=mandate.status,
        created_at=mandate.created_at
    )

# New Models
class UPIMandateRequest(BaseModel):
    merchant_id: str
    amount_limit: float = Field(..., gt=0, le=100000)
    frequency: str = Field(..., regex="^(DAILY|WEEKLY|MONTHLY)$")
    start_date: date
    end_date: date

class UPIMandateResponse(BaseModel):
    mandate_id: str
    npci_mandate_id: str
    status: str
    created_at: datetime

# Database Model
class UPIMandate(Base):
    __tablename__ = "upi_mandates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)
    npci_mandate_id = Column(String, unique=True, nullable=False)
    amount_limit = Column(Float, nullable=False)
    frequency = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Test Scenarios**:
1. Test mandate creation with valid parameters
2. Test mandate creation with invalid merchant
3. Test mandate modification
4. Test mandate cancellation
5. Test automatic debit processing
6. Test failure handling and retry logic
7. Test NPCI compliance validation

**Compliance Requirements**:
- NPCI AutoPay guidelines compliance
- Customer consent management
- Mandate registration with NPCI
- Transaction limit validation
- Data privacy regulations

---

## CR-002: Biometric Authentication for High-Value Transactions

**Description**: Implement biometric authentication (fingerprint and face recognition) for transactions above ₹50,000 with fallback to MPIN.

**Agent Analysis**:
- Pattern: `biometric_auth`
- Confidence: 0.92
- Keywords: ['biometric', 'fingerprint', 'face', 'authentication', 'high-value']
- Priority: High
- Complexity: Medium

**Implementation Suggestions**:

### Flutter Changes:
```dart
// Enhanced Authentication Service
class BiometricAuthService {
  static const MethodChannel _channel = MethodChannel('biometric_auth');
  
  static Future<bool> isBiometricAvailable() async {
    try {
      final LocalAuthentication localAuth = LocalAuthentication();
      return await localAuth.canCheckBiometrics;
    } catch (e) {
      return false;
    }
  }
  
  static Future<List<BiometricType>> getAvailableBiometrics() async {
    final LocalAuthentication localAuth = LocalAuthentication();
    return await localAuth.getAvailableBiometrics();
  }
  
  static Future<bool> authenticateWithBiometric({
    required String reason,
    bool fallbackToMPIN = true,
  }) async {
    try {
      final LocalAuthentication localAuth = LocalAuthentication();
      
      final bool isAuthenticated = await localAuth.authenticate(
        localizedFallbackTitle: 'Use MPIN',
        biometricOnly: !fallbackToMPIN,
        options: AuthenticationOptions(
          biometricOnly: !fallbackToMPIN,
          stickyAuth: true,
        ),
      );
      
      return isAuthenticated;
    } catch (e) {
      if (fallbackToMPIN) {
        return await _showMPINDialog();
      }
      return false;
    }
  }
  
  static Future<bool> _showMPINDialog() async {
    // Show MPIN input dialog
    return await showDialog<bool>(
      context: navigatorKey.currentContext!,
      builder: (context) => MPINDialog(),
    ) ?? false;
  }
}

// Enhanced Transaction Confirmation
class TransactionConfirmationPage extends StatefulWidget {
  final TransactionRequest transaction;
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          TransactionSummaryCard(transaction: transaction),
          
          if (transaction.amount > 50000) ...[
            BiometricAuthSection(),
            Text('Biometric authentication required for high-value transactions'),
          ],
          
          ElevatedButton(
            onPressed: () => _confirmTransaction(),
            child: Text('Confirm Transaction'),
          ),
        ],
      ),
    );
  }
  
  void _confirmTransaction() async {
    if (transaction.amount > 50000) {
      final isAuthenticated = await BiometricAuthService.authenticateWithBiometric(
        reason: 'Authenticate to confirm transaction of ₹${transaction.amount}',
        fallbackToMPIN: true,
      );
      
      if (!isAuthenticated) {
        _showError('Authentication failed');
        return;
      }
    }
    
    // Proceed with transaction
    context.read<TransactionBloc>().add(ConfirmTransactionEvent(transaction));
  }
}
```

### Python Changes:
```python
# Enhanced Authentication Endpoints
@router.post("/api/v1/auth/biometric/enable")
async def enable_biometric_auth(
    biometric_request: BiometricEnableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate current MPIN first
    if not MPINService.verify_mpin(current_user.id, biometric_request.mpin):
        raise HTTPException(status_code=400, detail="Invalid MPIN")
    
    # Generate and store biometric key
    biometric_key = BiometricService.generate_biometric_key()
    
    # Update user record
    UserService.enable_biometric_auth(
        db=db,
        user_id=current_user.id,
        biometric_key=biometric_key,
        device_id=biometric_request.device_id
    )
    
    return {"message": "Biometric authentication enabled successfully"}

@router.post("/api/v1/transactions/verify-high-value")
async def verify_high_value_transaction(
    verification_request: HighValueVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = TransactionService.get_pending_transaction(
        db, verification_request.transaction_id
    )
    
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.amount > 50000:
        # Verify biometric or MPIN
        if verification_request.biometric_data:
            is_valid = BiometricService.verify_biometric(
                user_id=current_user.id,
                biometric_data=verification_request.biometric_data,
                device_id=verification_request.device_id
            )
        elif verification_request.mpin:
            is_valid = MPINService.verify_mpin(current_user.id, verification_request.mpin)
        else:
            raise HTTPException(status_code=400, detail="Authentication required")
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    # Mark transaction as verified
    TransactionService.mark_verified(db, transaction.id)
    
    return {"message": "Transaction verified successfully"}

# Enhanced User Model
class User(Base):
    __tablename__ = "users"
    
    # ... existing fields ...
    biometric_enabled = Column(Boolean, default=False)
    biometric_key = Column(String, nullable=True)
    registered_device_id = Column(String, nullable=True)
    biometric_enabled_at = Column(DateTime, nullable=True)
```

**Test Scenarios**:
1. Test biometric authentication setup
2. Test fingerprint authentication for high-value transactions
3. Test face recognition authentication
4. Test fallback to MPIN when biometric fails
5. Test device binding for biometric authentication
6. Test biometric authentication disable/re-enable
7. Test security scenarios (multiple failed attempts)

---

## CR-003: Offline Aadhaar KYC using XML File

**Description**: Add offline Aadhaar KYC using XML file verification with digital signature validation and demographic data extraction.

**Agent Analysis**:
- Pattern: `kyc_enhancement`
- Confidence: 0.88
- Keywords: ['kyc', 'aadhaar', 'offline', 'xml', 'verification']
- Priority: High
- Complexity: High

**Implementation Suggestions**:

### Flutter Changes:
```dart
// New Offline KYC Page
class OfflineKYCPage extends StatefulWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Offline Aadhaar KYC')),
      body: Column(
        children: [
          InstructionCard(
            title: 'How to get Aadhaar XML?',
            instructions: [
              '1. Visit UIDAI website or mAadhaar app',
              '2. Download your Aadhaar XML file',
              '3. Use the same password you set while downloading',
            ],
          ),
          
          FilePickerSection(),
          PasswordInputSection(),
          
          ElevatedButton(
            onPressed: () => _processXMLFile(),
            child: Text('Verify KYC'),
          ),
        ],
      ),
    );
  }
  
  void _processXMLFile() async {
    if (selectedFile == null || passwordController.text.isEmpty) {
      _showError('Please select XML file and enter password');
      return;
    }
    
    try {
      // Read file as bytes
      final bytes = await selectedFile!.readAsBytes();
      final base64Content = base64Encode(bytes);
      
      final response = await dio.post('/api/v1/kyc/aadhaar/offline', data: {
        'xml_content': base64Content,
        'password': passwordController.text,
      });
      
      if (response.data['success']) {
        _showKYCSuccess(response.data['demographic_data']);
      }
    } catch (e) {
      _showError('KYC verification failed: ${e.toString()}');
    }
  }
}

// XML Parser Service
class AadhaarXMLParser {
  static Future<Map<String, dynamic>> parseXMLFile(
    Uint8List xmlBytes, 
    String password
  ) async {
    try {
      // Decrypt XML content
      final decryptedContent = await _decryptXML(xmlBytes, password);
      
      // Parse XML
      final document = XmlDocument.parse(decryptedContent);
      
      // Extract demographic data
      final demographicData = _extractDemographicData(document);
      
      // Verify digital signature
      final isSignatureValid = await _verifyDigitalSignature(document);
      
      return {
        'demographic_data': demographicData,
        'signature_valid': isSignatureValid,
        'aadhaar_number': _maskAadhaar(demographicData['aadhaar_number']),
      };
    } catch (e) {
      throw Exception('Failed to parse Aadhaar XML: $e');
    }
  }
  
  static Future<String> _decryptXML(Uint8List encryptedBytes, String password) async {
    // Implement ZIP decryption logic
    final archive = ZipDecoder().decodeBytes(encryptedBytes, password: password);
    final xmlFile = archive.files.firstWhere((file) => file.name.endsWith('.xml'));
    return utf8.decode(xmlFile.content);
  }
  
  static Map<String, dynamic> _extractDemographicData(XmlDocument document) {
    final root = document.rootElement;
    
    return {
      'name': root.getAttribute('name'),
      'gender': root.getAttribute('gender'),
      'date_of_birth': root.getAttribute('dob'),
      'address': _extractAddress(root),
      'aadhaar_number': root.getAttribute('uid'),
      'mobile': root.getAttribute('phone'),
      'email': root.getAttribute('email'),
    };
  }
}
```

### Python Changes:
```python
# New Offline KYC Endpoint
@router.post("/api/v1/kyc/aadhaar/offline")
async def process_offline_aadhaar_kyc(
    kyc_request: OfflineAadhaarKYCRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Decode base64 XML content
        xml_bytes = base64.b64decode(kyc_request.xml_content)
        
        # Parse and validate XML
        parser_result = AadhaarXMLParser.parse_xml(
            xml_bytes=xml_bytes,
            password=kyc_request.password
        )
        
        if not parser_result['signature_valid']:
            raise HTTPException(status_code=400, detail="Invalid digital signature")
        
        # Extract demographic data
        demographic_data = parser_result['demographic_data']
        
        # Validate Aadhaar number
        if not AadhaarValidator.validate(demographic_data['aadhaar_number']):
            raise HTTPException(status_code=400, detail="Invalid Aadhaar number in XML")
        
        # Store KYC data
        kyc_record = KYCService.create_offline_kyc_record(
            db=db,
            user_id=current_user.id,
            aadhaar_number=AadhaarValidator.mask_aadhaar(demographic_data['aadhaar_number']),
            demographic_data=demographic_data,
            verification_method='OFFLINE_XML',
            status=KYCStatus.COMPLETED
        )
        
        # Update user KYC level
        UserService.update_kyc_level(db, current_user.id, KYCLevel.FULL)
        
        return OfflineKYCResponse(
            success=True,
            kyc_id=kyc_record.id,
            demographic_data=demographic_data,
            kyc_level='FULL',
            message="Offline KYC completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Offline KYC failed for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"KYC processing failed: {str(e)}")

# XML Parser Service
class AadhaarXMLParser:
    @staticmethod
    def parse_xml(xml_bytes: bytes, password: str) -> Dict[str, Any]:
        try:
            # Decrypt ZIP file
            decrypted_content = AadhaarXMLParser._decrypt_zip(xml_bytes, password)
            
            # Parse XML
            root = ET.fromstring(decrypted_content)
            
            # Extract demographic data
            demographic_data = AadhaarXMLParser._extract_demographic_data(root)
            
            # Verify digital signature
            signature_valid = AadhaarXMLParser._verify_digital_signature(root)
            
            return {
                'demographic_data': demographic_data,
                'signature_valid': signature_valid
            }
            
        except Exception as e:
            raise ValueError(f"Failed to parse Aadhaar XML: {str(e)}")
    
    @staticmethod
    def _decrypt_zip(encrypted_bytes: bytes, password: str) -> str:
        import zipfile
        import io
        
        with zipfile.ZipFile(io.BytesIO(encrypted_bytes)) as zip_file:
            zip_file.setpassword(password.encode())
            xml_filename = [name for name in zip_file.namelist() if name.endswith('.xml')][0]
            return zip_file.read(xml_filename).decode('utf-8')
    
    @staticmethod
    def _verify_digital_signature(root: ET.Element) -> bool:
        # Implement UIDAI digital signature verification
        signature_element = root.find('.//Signature')
        if signature_element is None:
            return False
        
        # Verify against UIDAI public key
        return DigitalSignatureVerifier.verify_uidai_signature(root, signature_element)

# Models
class OfflineAadhaarKYCRequest(BaseModel):
    xml_content: str  # Base64 encoded XML file
    password: str

class OfflineKYCResponse(BaseModel):
    success: bool
    kyc_id: str
    demographic_data: Dict[str, Any]
    kyc_level: str
    message: str
```

**Test Scenarios**:
1. Test XML file upload and parsing
2. Test password validation for encrypted XML
3. Test digital signature verification
4. Test demographic data extraction
5. Test invalid XML file handling
6. Test corrupted file handling
7. Test KYC level upgrade after successful verification

---

## CR-004: Transaction Limits Based on KYC Level

**Description**: Implement transaction limits based on KYC level - Minimum KYC: ₹10,000/day, Full KYC: ₹1,00,000/day, Enhanced KYC: ₹10,00,000/day.

**Agent Analysis**:
- Pattern: `transaction_limits`
- Confidence: 0.91
- Keywords: ['limit', 'transaction', 'kyc', 'based']
- Priority: High
- Complexity: Medium

**Implementation Suggestions**:

### Flutter Changes:
```dart
// Enhanced Transaction Pages with Limit Display
class NEFTTransferPage extends StatefulWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<UserBloc, UserState>(
      builder: (context, userState) {
        final kycLevel = userState.user?.kycLevel ?? KYCLevel.MINIMUM;
        final dailyLimit = TransactionLimits.getDailyLimit(kycLevel, 'NEFT');
        final usedLimit = userState.user?.dailyTransactionAmount ?? 0.0;
        final availableLimit = dailyLimit - usedLimit;
        
        return Scaffold(
          body: Column(
            children: [
              TransactionLimitCard(
                kycLevel: kycLevel,
                dailyLimit: dailyLimit,
                usedLimit: usedLimit,
                availableLimit: availableLimit,
              ),
              
              if (availableLimit <= 0) ...[
                LimitExceededCard(),
                KYCUpgradePrompt(currentLevel: kycLevel),
              ] else ...[
                NEFTTransferForm(maxAmount: availableLimit),
              ],
            ],
          ),
        );
      },
    );
  }
}

// Transaction Limits Utility
class TransactionLimits {
  static const Map<KYCLevel, Map<String, double>> DAILY_LIMITS = {
    KYCLevel.MINIMUM: {
      'NEFT': 10000.0,
      'RTGS': 0.0,  // Not allowed
      'IMPS': 10000.0,
      'UPI': 10000.0,
    },
    KYCLevel.FULL: {
      'NEFT': 100000.0,
      'RTGS': 200000.0,
      'IMPS': 100000.0,
      'UPI': 100000.0,
    },
    KYCLevel.ENHANCED: {
      'NEFT': 1000000.0,
      'RTGS': 10000000.0,
      'IMPS': 500000.0,
      'UPI': 100000.0,
    },
  };
  
  static double getDailyLimit(KYCLevel kycLevel, String transactionType) {
    return DAILY_LIMITS[kycLevel]?[transactionType] ?? 0.0;
  }
  
  static bool isTransactionAllowed(
    KYCLevel kycLevel, 
    String transactionType, 
    double amount,
    double dailyUsed
  ) {
    final dailyLimit = getDailyLimit(kycLevel, transactionType);
    return (dailyUsed + amount) <= dailyLimit;
  }
}

// KYC Upgrade Prompt Widget
class KYCUpgradePrompt extends StatelessWidget {
  final KYCLevel currentLevel;
  
  @override
  Widget build(BuildContext context) {
    final nextLevel = _getNextKYCLevel(currentLevel);
    final nextLevelLimits = TransactionLimits.DAILY_LIMITS[nextLevel];
    
    return Card(
      color: Colors.orange.shade50,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(Icons.upgrade, color: Colors.orange, size: 48),
            Text('Upgrade your KYC to increase limits'),
            Text('Current: ${currentLevel.name}'),
            Text('Upgrade to: ${nextLevel.name}'),
            Text('New daily limit: ₹${nextLevelLimits?['NEFT']?.toStringAsFixed(0)}'),
            
            ElevatedButton(
              onPressed: () => Navigator.pushNamed(context, '/kyc-upgrade'),
              child: Text('Upgrade KYC'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Python Changes:
```python
# Enhanced Transaction Validation Service
class TransactionLimitService:
    DAILY_LIMITS = {
        KYCLevel.MINIMUM: {
            'NEFT': 10000.0,
            'RTGS': 0.0,
            'IMPS': 10000.0,
            'UPI': 10000.0,
        },
        KYCLevel.FULL: {
            'NEFT': 100000.0,
            'RTGS': 200000.0,
            'IMPS': 100000.0,
            'UPI': 100000.0,
        },
        KYCLevel.ENHANCED: {
            'NEFT': 1000000.0,
            'RTGS': 10000000.0,
            'IMPS': 500000.0,
            'UPI': 100000.0,
        }
    }
    
    @staticmethod
    def validate_transaction_limit(
        db: Session,
        user_id: str,
        transaction_type: str,
        amount: float
    ) -> Dict[str, Any]:
        # Get user's KYC level
        user = UserService.get_user(db, user_id)
        kyc_level = user.kyc_level
        
        # Get daily limit for transaction type
        daily_limit = TransactionLimitService.DAILY_LIMITS.get(kyc_level, {}).get(transaction_type, 0.0)
        
        if daily_limit == 0.0:
            return {
                'valid': False,
                'error': f'{transaction_type} not allowed for {kyc_level.value} KYC',
                'upgrade_required': True
            }
        
        # Check single transaction limit
        if amount > daily_limit:
            return {
                'valid': False,
                'error': f'Amount exceeds single transaction limit of ₹{daily_limit:,.2f}',
                'daily_limit': daily_limit,
                'upgrade_required': True
            }
        
        # Check daily cumulative limit
        today_total = TransactionService.get_daily_transaction_total(
            db, user_id, transaction_type, date.today()
        )
        
        if (today_total + amount) > daily_limit:
            remaining_limit = daily_limit - today_total
            return {
                'valid': False,
                'error': f'Daily limit exceeded. Remaining limit: ₹{remaining_limit:,.2f}',
                'daily_limit': daily_limit,
                'used_limit': today_total,
                'remaining_limit': remaining_limit,
                'upgrade_required': remaining_limit <= 0
            }
        
        return {
            'valid': True,
            'daily_limit': daily_limit,
            'used_limit': today_total,
            'remaining_limit': daily_limit - today_total - amount
        }

# Enhanced Transaction Endpoints
@router.post("/api/v1/transactions/neft")
async def create_neft_transaction(
    transaction_request: NEFTTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate KYC-based limits
    limit_validation = TransactionLimitService.validate_transaction_limit(
        db=db,
        user_id=current_user.id,
        transaction_type='NEFT',
        amount=transaction_request.amount
    )
    
    if not limit_validation['valid']:
        error_response = {
            'error': limit_validation['error'],
            'error_code': 'LIMIT_EXCEEDED'
        }
        
        if limit_validation.get('upgrade_required'):
            error_response.update({
                'upgrade_available': True,
                'current_kyc_level': current_user.kyc_level.value,
                'suggested_upgrade': KYCService.get_next_kyc_level(current_user.kyc_level).value
            })
        
        raise HTTPException(status_code=400, detail=error_response)
    
    # Proceed with transaction
    transaction = NEFTService.process_transaction(
        user_id=current_user.id,
        amount=transaction_request.amount,
        beneficiary_account=transaction_request.beneficiary_account,
        ifsc_code=transaction_request.ifsc_code
    )
    
    return NEFTTransactionResponse(
        transaction_id=transaction.id,
        status=transaction.status,
        remaining_daily_limit=limit_validation['remaining_limit']
    )

# KYC Level Validator
class KYCLevelValidator:
    @staticmethod
    def get_required_kyc_level(transaction_type: str, amount: float) -> KYCLevel:
        """Determine minimum KYC level required for transaction"""
        if transaction_type == 'RTGS':
            return KYCLevel.FULL  # RTGS requires at least Full KYC
        
        if amount > 100000:
            return KYCLevel.ENHANCED
        elif amount > 10000:
            return KYCLevel.FULL
        else:
            return KYCLevel.MINIMUM
    
    @staticmethod
    def can_perform_transaction(user_kyc_level: KYCLevel, required_level: KYCLevel) -> bool:
        """Check if user's KYC level is sufficient"""
        kyc_hierarchy = {
            KYCLevel.MINIMUM: 1,
            KYCLevel.FULL: 2,
            KYCLevel.ENHANCED: 3
        }
        
        return kyc_hierarchy[user_kyc_level] >= kyc_hierarchy[required_level]
```

**Test Scenarios**:
1. Test transaction within KYC limits
2. Test transaction exceeding single transaction limit
3. Test daily cumulative limit validation
4. Test KYC upgrade requirement scenarios
5. Test different transaction types with different KYC levels
6. Test limit reset at midnight
7. Test error messages and upgrade prompts

**Business Rules**:
- Minimum KYC: ₹10,000/day for NEFT, IMPS, UPI
- Full KYC: ₹1,00,000/day for NEFT, IMPS, UPI; ₹2,00,000 minimum for RTGS
- Enhanced KYC: ₹10,00,000/day for NEFT; ₹1,00,00,000/day for RTGS
- Limits reset daily at midnight
- Real-time limit tracking and validation
- Automatic KYC upgrade suggestions when limits are reached

This comprehensive implementation demonstrates how the FD Agent System analyzes change requests and provides detailed, actionable implementation suggestions that cover both frontend and backend changes, along with thorough testing scenarios and compliance considerations.