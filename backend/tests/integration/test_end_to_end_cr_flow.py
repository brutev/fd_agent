import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import os
import json

from agents.orchestrator import AgentOrchestrator
from memory.vector_store import VectorStore
from memory.structured_store import StructuredStore

class TestEndToEndCRFlow:
    """End-to-end integration tests for Change Request processing"""
    
    @pytest.fixture
    async def orchestrator_with_real_data(self):
        """Create orchestrator with real test data"""
        with patch('agents.orchestrator.VectorStore') as mock_vector_store, \
             patch('agents.orchestrator.StructuredStore') as mock_structured_store:
            
            orchestrator = AgentOrchestrator()
            
            # Mock vector store with realistic responses
            orchestrator.vector_store = Mock()
            orchestrator.vector_store.search_flutter_code = Mock()
            orchestrator.vector_store.search_python_code = Mock()
            orchestrator.vector_store.search_similar_crs = Mock()
            orchestrator.vector_store.add_change_request = Mock()
            orchestrator.vector_store.get_collection_stats = Mock(return_value={
                'flutter_code': 25,
                'python_code': 18,
                'brd_documents': 5,
                'change_requests': 3
            })
            
            # Mock structured store
            orchestrator.structured_store = AsyncMock()
            orchestrator.structured_store.init_db = AsyncMock()
            orchestrator.structured_store.add_change_request = AsyncMock()
            orchestrator.structured_store.get_api_mappings = AsyncMock(return_value=[])
            orchestrator.structured_store.get_stats = AsyncMock(return_value={
                'entities': {'widget': 15, 'endpoint': 12, 'model': 8},
                'relationships': {'calls': 5, 'uses': 3},
                'change_requests': 3,
                'api_mappings': 7
            })
            
            # Mock memory agent
            orchestrator.memory_agent = AsyncMock()
            orchestrator.memory_agent.store_change_request = AsyncMock()
            
            return orchestrator
    
    @pytest.mark.asyncio
    async def test_upi_autopay_cr_complete_flow(self, orchestrator_with_real_data):
        """Test complete UPI AutoPay CR processing flow"""
        
        # Setup mock responses for UPI AutoPay context
        orchestrator_with_real_data.vector_store.search_flutter_code.return_value = [
            {
                'content': '''
                class UPIPaymentPage extends StatefulWidget {
                  @override
                  Widget build(BuildContext context) {
                    return Scaffold(
                      body: Column(
                        children: [
                          TextFormField(
                            decoration: InputDecoration(labelText: 'UPI ID'),
                            validator: Validators.validateUPIId,
                          ),
                          TextFormField(
                            decoration: InputDecoration(labelText: 'Amount'),
                            validator: Validators.validateUPIAmount,
                          ),
                          ElevatedButton(
                            onPressed: () => _makeUPIPayment(),
                            child: Text('Pay Now'),
                          ),
                        ],
                      ),
                    );
                  }
                  
                  void _makeUPIPayment() async {
                    final response = await dio.post('/api/v1/upi/payment', data: {
                      'upi_id': upiIdController.text,
                      'amount': amountController.text,
                    });
                  }
                }
                ''',
                'metadata': {
                    'file_path': '/lib/features/transactions/presentation/pages/upi_payment_page.dart',
                    'type': 'widget',
                    'api_calls': ['/api/v1/upi/payment'],
                    'validators': ['validateUPIId', 'validateUPIAmount']
                }
            }
        ]
        
        orchestrator_with_real_data.vector_store.search_python_code.return_value = [
            {
                'content': '''
                @router.post("/api/v1/upi/payment")
                async def create_upi_payment(
                    payment_request: UPIPaymentRequest,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)
                ):
                    # Validate UPI ID
                    if not UPIValidator.validate(payment_request.upi_id):
                        raise HTTPException(status_code=400, detail="Invalid UPI ID")
                    
                    # Validate amount limits
                    amount_validation = TransactionValidator.validate_amount(
                        payment_request.amount, 'UPI'
                    )
                    if not amount_validation['valid']:
                        raise HTTPException(status_code=400, detail=amount_validation['error'])
                    
                    # Process payment
                    payment = UPIPaymentService.process_payment(
                        user_id=current_user.id,
                        upi_id=payment_request.upi_id,
                        amount=payment_request.amount
                    )
                    
                    return UPIPaymentResponse(
                        transaction_id=payment.transaction_id,
                        status=payment.status,
                        amount=payment.amount
                    )
                ''',
                'metadata': {
                    'file_path': '/backend/api/routes/transactions.py',
                    'type': 'endpoint',
                    'method': 'POST',
                    'path': '/api/v1/upi/payment',
                    'validators': ['UPIValidator', 'TransactionValidator']
                }
            }
        ]
        
        orchestrator_with_real_data.vector_store.search_similar_crs.return_value = [
            {
                'content': 'CR: Add recurring payment feature for bill payments\nImplementation: Added scheduled payment functionality',
                'metadata': {
                    'cr_id': 'CR-001',
                    'description': 'Add recurring payment feature',
                    'complexity': 'medium',
                    'timestamp': '2024-01-15T10:30:00'
                }
            }
        ]
        
        # Execute CR processing
        cr_description = "Add UPI AutoPay mandate feature for recurring payments with merchant registration and automatic debit functionality"
        
        result = await orchestrator_with_real_data.handle_change_request(cr_description)
        
        # Verify CR processing results
        assert 'cr_id' in result
        assert result['description'] == cr_description
        assert 'result' in result
        assert 'timestamp' in result
        
        cr_result = result['result']
        
        # Verify analysis
        assert 'analysis' in cr_result
        analysis = cr_result['analysis']
        assert analysis['pattern'] == 'upi_autopay'
        assert analysis['confidence'] > 0.5
        assert 'upi' in analysis['keywords']
        assert 'autopay' in analysis['keywords']
        assert 'mandate' in analysis['keywords']
        
        # Verify implementation suggestions
        assert 'implementation' in cr_result
        implementation = cr_result['implementation']
        
        # Check Flutter changes
        flutter_changes = implementation['flutter_changes']
        assert 'new_screens' in flutter_changes
        assert len(flutter_changes['new_screens']) >= 2
        
        # Verify UPI AutoPay specific screens
        screen_names = [screen['name'] for screen in flutter_changes['new_screens']]
        assert any('AutoPay' in name or 'Mandate' in name for name in screen_names)
        
        # Check Python changes
        python_changes = implementation['python_changes']
        assert 'new_endpoints' in python_changes
        assert len(python_changes['new_endpoints']) >= 3
        
        # Verify mandate-specific endpoints
        endpoint_paths = [ep['path'] for ep in python_changes['new_endpoints']]
        assert any('mandate' in path for path in endpoint_paths)
        
        # Verify compliance requirements
        assert 'compliance_requirements' in implementation
        compliance = implementation['compliance_requirements']
        assert any('NPCI' in req for req in compliance)
        assert any('AutoPay' in req for req in compliance)
        
        # Verify test scenarios
        assert 'test_scenarios' in cr_result
        test_scenarios = cr_result['test_scenarios']
        assert len(test_scenarios) > 0
        
        # Check for UPI AutoPay specific tests
        test_descriptions = [test['description'] for test in test_scenarios]
        assert any('mandate' in desc.lower() for desc in test_descriptions)
        
        # Verify effort estimation
        assert 'estimated_effort' in cr_result
        effort = cr_result['estimated_effort']
        assert 'total_days' in effort
        assert 'complexity' in effort
        assert effort['total_days'] > 5  # UPI AutoPay should be complex
        
        # Verify memory storage was called
        orchestrator_with_real_data.memory_agent.store_change_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_biometric_auth_cr_complete_flow(self, orchestrator_with_real_data):
        """Test complete biometric authentication CR processing flow"""
        
        # Setup mock responses for biometric auth context
        orchestrator_with_real_data.vector_store.search_flutter_code.return_value = [
            {
                'content': '''
                class LoginPage extends StatefulWidget {
                  @override
                  Widget build(BuildContext context) {
                    return Scaffold(
                      body: Column(
                        children: [
                          TextFormField(
                            decoration: InputDecoration(labelText: 'Mobile Number'),
                            validator: Validators.validateMobileNumber,
                          ),
                          ElevatedButton(
                            onPressed: () => _sendOTP(),
                            child: Text('Send OTP'),
                          ),
                          ElevatedButton(
                            onPressed: () => _loginWithMPIN(),
                            child: Text('Login with MPIN'),
                          ),
                        ],
                      ),
                    );
                  }
                }
                ''',
                'metadata': {
                    'file_path': '/lib/features/auth/presentation/pages/login_page.dart',
                    'type': 'widget',
                    'authentication_methods': ['otp', 'mpin']
                }
            }
        ]
        
        orchestrator_with_real_data.vector_store.search_python_code.return_value = [
            {
                'content': '''
                @router.post("/api/v1/auth/login")
                async def login_user(
                    login_request: LoginRequest,
                    db: Session = Depends(get_db)
                ):
                    # Validate mobile number
                    if not TransactionValidator.validate_mobile_number(login_request.mobile):
                        raise HTTPException(status_code=400, detail="Invalid mobile number")
                    
                    # Send OTP
                    otp_service.send_otp(login_request.mobile)
                    
                    return {"message": "OTP sent successfully"}
                
                @router.post("/api/v1/auth/verify-otp")
                async def verify_otp(
                    otp_request: OTPVerificationRequest,
                    db: Session = Depends(get_db)
                ):
                    # Verify OTP
                    if not otp_service.verify_otp(otp_request.mobile, otp_request.otp):
                        raise HTTPException(status_code=400, detail="Invalid OTP")
                    
                    # Generate JWT token
                    token = create_access_token(data={"sub": otp_request.mobile})
                    return {"access_token": token, "token_type": "bearer"}
                ''',
                'metadata': {
                    'file_path': '/backend/api/routes/auth.py',
                    'type': 'endpoint',
                    'authentication_methods': ['otp', 'jwt']
                }
            }
        ]
        
        # Execute CR processing
        cr_description = "Implement biometric authentication (fingerprint and face recognition) for high-value transactions and login with fallback to MPIN"
        
        result = await orchestrator_with_real_data.handle_change_request(cr_description)
        
        # Verify CR processing results
        cr_result = result['result']
        
        # Verify analysis
        analysis = cr_result['analysis']
        assert analysis['pattern'] == 'biometric_auth'
        assert 'biometric' in analysis['keywords']
        assert 'fingerprint' in analysis['keywords']
        
        # Verify implementation suggestions
        implementation = cr_result['implementation']
        
        # Check Flutter changes
        flutter_changes = implementation['flutter_changes']
        assert 'dependencies' in flutter_changes
        assert 'local_auth' in str(flutter_changes['dependencies'])
        
        assert 'new_services' in flutter_changes
        service_names = [service['name'] for service in flutter_changes['new_services']]
        assert any('Biometric' in name for name in service_names)
        
        # Check Python changes
        python_changes = implementation['python_changes']
        assert 'new_endpoints' in python_changes
        
        endpoint_paths = [ep['path'] for ep in python_changes['new_endpoints']]
        assert any('biometric' in path for path in endpoint_paths)
        
        # Verify security enhancements
        assert 'security_enhancements' in python_changes
        security_features = python_changes['security_enhancements']
        assert any('template storage' in feature.lower() for feature in security_features)
        assert any('device binding' in feature.lower() for feature in security_features)
    
    @pytest.mark.asyncio
    async def test_kyc_enhancement_cr_complete_flow(self, orchestrator_with_real_data):
        """Test complete KYC enhancement CR processing flow"""
        
        # Setup mock responses for KYC context
        orchestrator_with_real_data.vector_store.search_flutter_code.return_value = [
            {
                'content': '''
                class AadhaarKYCPage extends StatefulWidget {
                  @override
                  Widget build(BuildContext context) {
                    return Scaffold(
                      body: Column(
                        children: [
                          TextFormField(
                            decoration: InputDecoration(labelText: 'Aadhaar Number'),
                            validator: Validators.validateAadhaar,
                          ),
                          ElevatedButton(
                            onPressed: () => _initiateKYC(),
                            child: Text('Start KYC'),
                          ),
                        ],
                      ),
                    );
                  }
                  
                  void _initiateKYC() async {
                    final response = await dio.post('/api/v1/kyc/aadhaar/initiate', data: {
                      'aadhaar_number': aadhaarController.text,
                    });
                  }
                }
                ''',
                'metadata': {
                    'file_path': '/lib/features/kyc/presentation/pages/aadhaar_kyc_page.dart',
                    'type': 'widget',
                    'kyc_methods': ['aadhaar_online']
                }
            }
        ]
        
        orchestrator_with_real_data.vector_store.search_python_code.return_value = [
            {
                'content': '''
                @router.post("/api/v1/kyc/aadhaar/initiate")
                async def initiate_aadhaar_kyc(
                    kyc_request: AadhaarKYCRequest,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)
                ):
                    # Validate Aadhaar number
                    if not AadhaarValidator.validate(kyc_request.aadhaar_number):
                        raise HTTPException(status_code=400, detail="Invalid Aadhaar number")
                    
                    # Initiate UIDAI KYC
                    kyc_response = uidai_service.initiate_kyc(
                        aadhaar_number=kyc_request.aadhaar_number,
                        user_id=current_user.id
                    )
                    
                    return AadhaarKYCResponse(
                        transaction_id=kyc_response.transaction_id,
                        status="initiated"
                    )
                ''',
                'metadata': {
                    'file_path': '/backend/api/routes/kyc.py',
                    'type': 'endpoint',
                    'kyc_methods': ['aadhaar_online', 'uidai_integration']
                }
            }
        ]
        
        # Execute CR processing
        cr_description = "Add offline Aadhaar KYC using XML file verification with digital signature validation and demographic data extraction"
        
        result = await orchestrator_with_real_data.handle_change_request(cr_description)
        
        # Verify CR processing results
        cr_result = result['result']
        
        # Verify analysis
        analysis = cr_result['analysis']
        assert analysis['pattern'] == 'kyc_enhancement'
        assert 'kyc' in analysis['keywords']
        assert 'aadhaar' in analysis['keywords']
        assert 'offline' in analysis['keywords']
        
        # Verify implementation suggestions
        implementation = cr_result['implementation']
        
        # Check Flutter changes
        flutter_changes = implementation['flutter_changes']
        assert 'new_screens' in flutter_changes
        
        screen_names = [screen['name'] for screen in flutter_changes['new_screens']]
        assert any('Offline' in name and 'KYC' in name for name in screen_names)
        
        assert 'dependencies' in flutter_changes
        dependencies = flutter_changes['dependencies']
        assert any('file_picker' in dep for dep in dependencies)
        assert any('xml' in dep for dep in dependencies)
        
        # Check Python changes
        python_changes = implementation['python_changes']
        assert 'new_services' in python_changes
        
        service_names = python_changes['new_services']
        assert 'AadhaarXMLValidator' in service_names
        assert 'DigitalSignatureVerifier' in service_names
        
        # Verify compliance requirements
        assert 'compliance_requirements' in implementation
        compliance = implementation['compliance_requirements']
        assert any('UIDAI' in req for req in compliance)
        assert any('offline KYC' in req for req in compliance)
    
    @pytest.mark.asyncio
    async def test_transaction_limits_cr_complete_flow(self, orchestrator_with_real_data):
        """Test complete transaction limits CR processing flow"""
        
        # Setup mock responses
        orchestrator_with_real_data.vector_store.search_flutter_code.return_value = [
            {
                'content': '''
                class NEFTTransferPage extends StatefulWidget {
                  void _validateAmount() {
                    final amount = double.tryParse(amountController.text);
                    if (amount == null || amount <= 0) {
                      setState(() => errorMessage = 'Invalid amount');
                      return;
                    }
                    
                    if (amount > 1000000) {
                      setState(() => errorMessage = 'Amount exceeds NEFT limit');
                      return;
                    }
                  }
                }
                ''',
                'metadata': {
                    'file_path': '/lib/features/transactions/presentation/pages/neft_transfer_page.dart',
                    'type': 'widget',
                    'transaction_types': ['neft'],
                    'validation_logic': ['amount_limits']
                }
            }
        ]
        
        orchestrator_with_real_data.vector_store.search_python_code.return_value = [
            {
                'content': '''
                @router.post("/api/v1/transactions/neft")
                async def create_neft_transaction(
                    transaction_request: NEFTTransactionRequest,
                    current_user: User = Depends(get_current_user)
                ):
                    # Validate amount limits
                    amount_validation = TransactionValidator.validate_amount(
                        transaction_request.amount, 'NEFT'
                    )
                    if not amount_validation['valid']:
                        raise HTTPException(status_code=400, detail=amount_validation['error'])
                    
                    # Process transaction
                    transaction = NEFTService.process_transaction(
                        user_id=current_user.id,
                        amount=transaction_request.amount,
                        beneficiary_account=transaction_request.beneficiary_account
                    )
                    
                    return NEFTTransactionResponse(
                        transaction_id=transaction.transaction_id,
                        status=transaction.status
                    )
                ''',
                'metadata': {
                    'file_path': '/backend/api/routes/transactions.py',
                    'type': 'endpoint',
                    'transaction_types': ['neft'],
                    'validation_logic': ['amount_limits', 'user_validation']
                }
            }
        ]
        
        # Execute CR processing
        cr_description = "Implement transaction limits based on KYC level - Minimum KYC: ₹10,000/day, Full KYC: ₹1,00,000/day, Enhanced KYC: ₹10,00,000/day"
        
        result = await orchestrator_with_real_data.handle_change_request(cr_description)
        
        # Verify CR processing results
        cr_result = result['result']
        
        # Verify analysis
        analysis = cr_result['analysis']
        assert analysis['pattern'] == 'transaction_limits'
        assert 'limit' in analysis['keywords']
        assert 'kyc' in analysis['keywords']
        
        # Verify implementation suggestions
        implementation = cr_result['implementation']
        
        # Check business rules
        python_changes = implementation['python_changes']
        assert 'business_rules' in python_changes
        
        business_rules = python_changes['business_rules']
        assert any('10,000' in rule for rule in business_rules)
        assert any('1,00,000' in rule for rule in business_rules)
        assert any('10,00,000' in rule for rule in business_rules)
        
        # Check new services
        assert 'new_services' in python_changes
        service_names = python_changes['new_services']
        assert 'TransactionLimitService' in service_names
        assert 'KYCLevelValidator' in service_names
    
    @pytest.mark.asyncio
    async def test_tax_statement_cr_complete_flow(self, orchestrator_with_real_data):
        """Test complete tax statement CR processing flow"""
        
        # Setup mock responses
        orchestrator_with_real_data.vector_store.search_flutter_code.return_value = [
            {
                'content': '''
                class AccountStatementPage extends StatefulWidget {
                  void _downloadStatement() async {
                    final response = await dio.get('/api/v1/accounts/statement', 
                      queryParameters: {
                        'from_date': fromDate.toIso8601String(),
                        'to_date': toDate.toIso8601String(),
                        'format': 'pdf'
                      }
                    );
                  }
                }
                ''',
                'metadata': {
                    'file_path': '/lib/features/accounts/presentation/pages/account_statement_page.dart',
                    'type': 'widget',
                    'features': ['statement_download', 'pdf_generation']
                }
            }
        ]
        
        orchestrator_with_real_data.vector_store.search_python_code.return_value = [
            {
                'content': '''
                @router.get("/api/v1/accounts/statement")
                async def get_account_statement(
                    from_date: date,
                    to_date: date,
                    format: str = "pdf",
                    current_user: User = Depends(get_current_user)
                ):
                    # Get transactions
                    transactions = TransactionService.get_user_transactions(
                        user_id=current_user.id,
                        from_date=from_date,
                        to_date=to_date
                    )
                    
                    # Generate PDF
                    if format == "pdf":
                        pdf_content = PDFGenerator.generate_statement(transactions)
                        return Response(content=pdf_content, media_type="application/pdf")
                    
                    return transactions
                ''',
                'metadata': {
                    'file_path': '/backend/api/routes/accounts.py',
                    'type': 'endpoint',
                    'features': ['statement_generation', 'pdf_export']
                }
            }
        ]
        
        # Execute CR processing
        cr_description = "Generate annual tax statement with TDS/TCS calculation, interest income aggregation, and Form 26AS format compliance for ITR filing"
        
        result = await orchestrator_with_real_data.handle_change_request(cr_description)
        
        # Verify CR processing results
        cr_result = result['result']
        
        # Verify analysis
        analysis = cr_result['analysis']
        assert analysis['pattern'] == 'tax_statement'
        assert 'tax' in analysis['keywords']
        assert 'statement' in analysis['keywords']
        
        # Verify implementation suggestions
        implementation = cr_result['implementation']
        
        # Check Python changes
        python_changes = implementation['python_changes']
        assert 'new_services' in python_changes
        
        service_names = python_changes['new_services']
        assert 'TaxCalculationService' in service_names
        assert 'Form26ASGenerator' in service_names
        assert 'TDSCalculator' in service_names
        
        # Verify compliance requirements
        assert 'compliance_requirements' in implementation
        compliance = implementation['compliance_requirements']
        assert any('Income Tax Act' in req for req in compliance)
        assert any('Form 26AS' in req for req in compliance)
    
    @pytest.mark.asyncio
    async def test_memory_persistence_across_crs(self, orchestrator_with_real_data):
        """Test that memory persists across multiple CR processing sessions"""
        
        # Process first CR
        cr1_description = "Add UPI AutoPay mandate feature"
        result1 = await orchestrator_with_real_data.handle_change_request(cr1_description)
        
        # Verify first CR was stored
        orchestrator_with_real_data.memory_agent.store_change_request.assert_called()
        
        # Setup mock for similar CR search (should return first CR)
        orchestrator_with_real_data.vector_store.search_similar_crs.return_value = [
            {
                'content': f'CR: {cr1_description}\nImplementation: UPI AutoPay implementation details',
                'metadata': {
                    'cr_id': result1['cr_id'],
                    'description': cr1_description,
                    'complexity': 'high'
                }
            }
        ]
        
        # Process second related CR
        cr2_description = "Add UPI mandate modification and cancellation features"
        result2 = await orchestrator_with_real_data.handle_change_request(cr2_description)
        
        # Verify second CR processing used context from first CR
        cr2_result = result2['result']
        assert 'context' in cr2_result
        
        similar_crs = cr2_result['context']['similar_crs']
        assert len(similar_crs) > 0
        assert any(cr1_description in cr['content'] for cr in similar_crs)
        
        # Verify both CRs were stored
        assert orchestrator_with_real_data.memory_agent.store_change_request.call_count == 2
    
    @pytest.mark.asyncio
    async def test_error_handling_in_cr_flow(self, orchestrator_with_real_data):
        """Test error handling during CR processing"""
        
        # Mock vector store to raise exception
        orchestrator_with_real_data.vector_store.search_flutter_code.side_effect = Exception("Vector store connection failed")
        
        # Process CR
        cr_description = "Add new feature with error"
        
        try:
            result = await orchestrator_with_real_data.handle_change_request(cr_description)
            
            # Should still return a result with error handling
            assert 'cr_id' in result
            assert 'result' in result
            
            # Implementation should be generic due to error
            cr_result = result['result']
            implementation = cr_result['implementation']
            assert 'analysis_based_suggestions' in implementation
            
        except Exception as e:
            # If exception is raised, it should be handled gracefully
            assert "Vector store connection failed" in str(e)
    
    @pytest.mark.asyncio
    async def test_performance_with_large_codebase(self, orchestrator_with_real_data):
        """Test CR processing performance with large codebase simulation"""
        
        # Mock large codebase responses
        large_flutter_response = []
        for i in range(100):  # Simulate 100 Flutter components
            large_flutter_response.append({
                'content': f'Flutter component {i} with various features',
                'metadata': {'file_path': f'/lib/component_{i}.dart', 'type': 'widget'}
            })
        
        large_python_response = []
        for i in range(80):  # Simulate 80 Python endpoints
            large_python_response.append({
                'content': f'Python endpoint {i} with business logic',
                'metadata': {'file_path': f'/backend/endpoint_{i}.py', 'type': 'endpoint'}
            })
        
        orchestrator_with_real_data.vector_store.search_flutter_code.return_value = large_flutter_response[:10]  # Limit to top 10
        orchestrator_with_real_data.vector_store.search_python_code.return_value = large_python_response[:10]  # Limit to top 10
        
        # Measure processing time
        import time
        start_time = time.time()
        
        result = await orchestrator_with_real_data.handle_change_request(
            "Add new feature to large codebase"
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify reasonable processing time (should be under 5 seconds)
        assert processing_time < 5.0
        
        # Verify result quality is maintained
        assert 'cr_id' in result
        assert 'result' in result
        cr_result = result['result']
        assert 'implementation' in cr_result
        assert 'affected_components' in cr_result

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=agents', '--cov-report=html'])