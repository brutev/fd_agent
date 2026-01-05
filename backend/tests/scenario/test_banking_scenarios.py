import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, time

from agents.orchestrator import AgentOrchestrator

class TestBankingScenarios:
    """Comprehensive scenario tests for Indian banking use cases"""
    
    @pytest.fixture
    async def banking_orchestrator(self):
        """Create orchestrator configured for banking scenarios"""
        with patch('agents.orchestrator.VectorStore') as mock_vector_store, \
             patch('agents.orchestrator.StructuredStore') as mock_structured_store:
            
            orchestrator = AgentOrchestrator()
            
            # Setup banking-specific mock data
            orchestrator.vector_store = Mock()
            orchestrator.structured_store = AsyncMock()
            orchestrator.memory_agent = AsyncMock()
            
            # Mock banking codebase
            orchestrator.vector_store.search_flutter_code.return_value = self._get_banking_flutter_context()
            orchestrator.vector_store.search_python_code.return_value = self._get_banking_python_context()
            orchestrator.vector_store.search_similar_crs.return_value = []
            orchestrator.vector_store.get_collection_stats.return_value = {
                'flutter_code': 45, 'python_code': 32, 'brd_documents': 8, 'change_requests': 12
            }
            
            orchestrator.structured_store.init_db = AsyncMock()
            orchestrator.structured_store.get_stats = AsyncMock(return_value={
                'entities': {'widget': 25, 'endpoint': 18, 'model': 12},
                'relationships': {'calls': 15, 'uses': 8},
                'change_requests': 12,
                'api_mappings': 20
            })
            orchestrator.structured_store.get_api_mappings = AsyncMock(return_value=[])
            orchestrator.memory_agent.store_change_request = AsyncMock()
            
            return orchestrator
    
    def _get_banking_flutter_context(self):
        """Get banking-specific Flutter context"""
        return [
            {
                'content': '''
                class AccountDashboard extends StatefulWidget {
                  @override
                  Widget build(BuildContext context) {
                    return Scaffold(
                      body: Column(
                        children: [
                          AccountBalanceCard(),
                          QuickActionsGrid(),
                          RecentTransactionsList(),
                          ServicesGrid(),
                        ],
                      ),
                    );
                  }
                }
                
                class AccountBalanceCard extends StatelessWidget {
                  Widget build(BuildContext context) {
                    return BlocBuilder<AccountBloc, AccountState>(
                      builder: (context, state) {
                        if (state is AccountLoaded) {
                          return Card(
                            child: Column(
                              children: [
                                Text('Account Balance'),
                                Text('₹${state.account.balance.toStringAsFixed(2)}'),
                                Text('Available Balance: ₹${state.account.availableBalance.toStringAsFixed(2)}'),
                              ],
                            ),
                          );
                        }
                        return CircularProgressIndicator();
                      },
                    );
                  }
                }
                ''',
                'metadata': {
                    'file_path': '/lib/features/accounts/presentation/pages/account_dashboard.dart',
                    'type': 'widget',
                    'features': ['account_balance', 'dashboard', 'bloc_pattern']
                }
            },
            {
                'content': '''
                class TransactionHistoryPage extends StatefulWidget {
                  @override
                  Widget build(BuildContext context) {
                    return Scaffold(
                      appBar: AppBar(title: Text('Transaction History')),
                      body: Column(
                        children: [
                          DateRangeSelector(),
                          TransactionFilters(),
                          Expanded(
                            child: BlocBuilder<TransactionBloc, TransactionState>(
                              builder: (context, state) {
                                if (state is TransactionsLoaded) {
                                  return ListView.builder(
                                    itemCount: state.transactions.length,
                                    itemBuilder: (context, index) {
                                      return TransactionCard(
                                        transaction: state.transactions[index],
                                      );
                                    },
                                  );
                                }
                                return CircularProgressIndicator();
                              },
                            ),
                          ),
                        ],
                      ),
                    );
                  }
                }
                ''',
                'metadata': {
                    'file_path': '/lib/features/transactions/presentation/pages/transaction_history_page.dart',
                    'type': 'widget',
                    'features': ['transaction_history', 'filtering', 'pagination']
                }
            },
            {
                'content': '''
                class KYCVerificationPage extends StatefulWidget {
                  @override
                  Widget build(BuildContext context) {
                    return Scaffold(
                      body: Column(
                        children: [
                          KYCStatusCard(),
                          if (kycStatus != KYCStatus.completed) ...[
                            AadhaarVerificationSection(),
                            PANVerificationSection(),
                            DocumentUploadSection(),
                          ],
                          if (kycStatus == KYCStatus.completed)
                            KYCCompletedSection(),
                        ],
                      ),
                    );
                  }
                  
                  void _initiateAadhaarKYC() async {
                    final response = await dio.post('/api/v1/kyc/aadhaar/initiate', data: {
                      'aadhaar_number': aadhaarController.text,
                    });
                  }
                }
                ''',
                'metadata': {
                    'file_path': '/lib/features/kyc/presentation/pages/kyc_verification_page.dart',
                    'type': 'widget',
                    'features': ['kyc_verification', 'aadhaar_kyc', 'pan_verification', 'document_upload']
                }
            }
        ]
    
    def _get_banking_python_context(self):
        """Get banking-specific Python context"""
        return [
            {
                'content': '''
                @router.get("/api/v1/accounts/{account_id}/balance")
                async def get_account_balance(
                    account_id: str,
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)
                ):
                    # Verify account ownership
                    account = AccountService.get_user_account(db, current_user.id, account_id)
                    if not account:
                        raise HTTPException(status_code=404, detail="Account not found")
                    
                    # Get real-time balance
                    balance = AccountService.get_account_balance(db, account_id)
                    available_balance = AccountService.get_available_balance(db, account_id)
                    
                    return AccountBalanceResponse(
                        account_id=account_id,
                        balance=balance,
                        available_balance=available_balance,
                        currency="INR",
                        last_updated=datetime.now()
                    )
                ''',
                'metadata': {
                    'file_path': '/backend/api/routes/accounts.py',
                    'type': 'endpoint',
                    'features': ['account_balance', 'real_time_data', 'security_validation']
                }
            },
            {
                'content': '''
                @router.post("/api/v1/transactions/neft")
                async def create_neft_transaction(
                    transaction_request: NEFTTransactionRequest,
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)
                ):
                    # Validate transaction limits based on KYC level
                    kyc_level = KYCService.get_user_kyc_level(db, current_user.id)
                    daily_limit = TransactionLimitService.get_daily_limit(kyc_level, 'NEFT')
                    
                    if transaction_request.amount > daily_limit:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Amount exceeds daily limit of ₹{daily_limit}"
                        )
                    
                    # Validate operating hours
                    current_time = datetime.now().time()
                    if not (time(8, 0) <= current_time <= time(19, 0)):
                        raise HTTPException(
                            status_code=400,
                            detail="NEFT transactions are available from 8:00 AM to 7:00 PM"
                        )
                    
                    # Validate IFSC code
                    if not IFSCValidator.validate(transaction_request.ifsc_code):
                        raise HTTPException(status_code=400, detail="Invalid IFSC code")
                    
                    # Process transaction
                    transaction = NEFTService.process_transaction(
                        user_id=current_user.id,
                        amount=transaction_request.amount,
                        beneficiary_account=transaction_request.beneficiary_account,
                        ifsc_code=transaction_request.ifsc_code,
                        remarks=transaction_request.remarks
                    )
                    
                    # Send notification
                    NotificationService.send_transaction_notification(
                        user_id=current_user.id,
                        transaction_id=transaction.id,
                        amount=transaction.amount,
                        type='NEFT'
                    )
                    
                    return NEFTTransactionResponse(
                        transaction_id=transaction.id,
                        status=transaction.status,
                        amount=transaction.amount,
                        charges=transaction.charges,
                        estimated_completion=transaction.estimated_completion
                    )
                ''',
                'metadata': {
                    'file_path': '/backend/api/routes/transactions.py',
                    'type': 'endpoint',
                    'features': ['neft_transfer', 'kyc_based_limits', 'operating_hours', 'validation', 'notifications']
                }
            },
            {
                'content': '''
                @router.post("/api/v1/kyc/aadhaar/initiate")
                async def initiate_aadhaar_kyc(
                    kyc_request: AadhaarKYCRequest,
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)
                ):
                    # Validate Aadhaar number using Verhoeff algorithm
                    if not AadhaarValidator.validate(kyc_request.aadhaar_number):
                        raise HTTPException(status_code=400, detail="Invalid Aadhaar number")
                    
                    # Check if KYC already completed
                    existing_kyc = KYCService.get_user_kyc(db, current_user.id)
                    if existing_kyc and existing_kyc.status == KYCStatus.COMPLETED:
                        raise HTTPException(status_code=400, detail="KYC already completed")
                    
                    # Initiate UIDAI KYC process
                    try:
                        kyc_response = UidaiService.initiate_aadhaar_kyc(
                            aadhaar_number=kyc_request.aadhaar_number,
                            consent=kyc_request.consent
                        )
                        
                        # Store KYC transaction
                        kyc_transaction = KYCService.create_kyc_transaction(
                            db=db,
                            user_id=current_user.id,
                            aadhaar_number=AadhaarValidator.mask_aadhaar(kyc_request.aadhaar_number),
                            transaction_id=kyc_response.transaction_id,
                            status=KYCStatus.INITIATED
                        )
                        
                        return AadhaarKYCResponse(
                            transaction_id=kyc_response.transaction_id,
                            status="initiated",
                            otp_sent=True,
                            message="OTP sent to Aadhaar registered mobile number"
                        )
                        
                    except UidaiServiceException as e:
                        raise HTTPException(status_code=400, detail=str(e))
                ''',
                'metadata': {
                    'file_path': '/backend/api/routes/kyc.py',
                    'type': 'endpoint',
                    'features': ['aadhaar_kyc', 'uidai_integration', 'validation', 'privacy_protection']
                }
            }
        ]
    
    @pytest.mark.asyncio
    async def test_account_balance_inquiry_scenario(self, banking_orchestrator):
        """Test account balance inquiry enhancement scenario"""
        
        cr_description = """
        Enhance account balance display to show:
        1. Real-time balance with last update timestamp
        2. Available balance (excluding holds/freezes)
        3. Monthly average balance
        4. Balance trend graph (last 6 months)
        5. Auto-refresh every 30 seconds
        6. Offline balance caching for poor network
        """
        
        result = await banking_orchestrator.handle_change_request(cr_description)
        
        # Verify CR processing
        assert 'cr_id' in result
        cr_result = result['result']
        
        # Verify analysis identifies account-related pattern
        analysis = cr_result['analysis']
        assert 'account' in analysis['keywords']
        assert 'balance' in analysis['keywords']
        assert 'real-time' in analysis['keywords']
        
        # Verify implementation suggestions
        implementation = cr_result['implementation']
        
        # Check Flutter changes
        flutter_changes = implementation.get('flutter_changes', {})
        if 'modified_screens' in flutter_changes:
            modified_screens = flutter_changes['modified_screens']
            assert any('Dashboard' in screen.get('name', '') or 'Account' in screen.get('name', '') 
                     for screen in modified_screens)
        
        # Check Python changes
        python_changes = implementation.get('python_changes', {})
        if 'modified_endpoints' in python_changes:
            endpoints = python_changes['modified_endpoints']
            assert any('balance' in str(endpoint).lower() for endpoint in endpoints)
        
        # Verify test scenarios include balance-specific tests
        test_scenarios = cr_result['test_scenarios']
        test_descriptions = [test['description'] for test in test_scenarios]
        assert any('balance' in desc.lower() for desc in test_descriptions)
    
    @pytest.mark.asyncio
    async def test_transaction_receipt_enhancement_scenario(self, banking_orchestrator):
        """Test transaction receipt enhancement scenario"""
        
        cr_description = """
        Enhance transaction receipts with:
        1. QR code for verification
        2. Digital signature for authenticity
        3. Detailed breakdown (charges, taxes, net amount)
        4. Compliance with RBI guidelines
        5. Multi-language support (English, Hindi, Regional)
        6. Email and SMS sharing options
        7. PDF download with bank letterhead
        """
        
        result = await banking_orchestrator.handle_change_request(cr_description)
        
        cr_result = result['result']
        
        # Verify analysis
        analysis = cr_result['analysis']
        assert 'receipt' in analysis['keywords'] or 'transaction' in analysis['keywords']
        
        # Verify implementation includes receipt enhancements
        implementation = cr_result['implementation']
        
        # Should suggest PDF generation improvements
        if 'python_changes' in implementation:
            python_changes = implementation['python_changes']
            if 'new_services' in python_changes:
                services = python_changes['new_services']
                assert any('PDF' in str(service) or 'Receipt' in str(service) for service in services)
        
        # Should include compliance considerations
        if 'compliance_requirements' in implementation:
            compliance = implementation['compliance_requirements']
            assert any('RBI' in req for req in compliance)
    
    @pytest.mark.asyncio
    async def test_fraud_detection_scenario(self, banking_orchestrator):
        """Test fraud detection system enhancement scenario"""
        
        cr_description = """
        Implement real-time fraud detection system:
        1. Unusual transaction pattern detection
        2. Device fingerprinting and geolocation validation
        3. Velocity checks (multiple transactions in short time)
        4. Amount-based risk scoring
        5. Machine learning model for fraud prediction
        6. Automatic transaction blocking for high-risk transactions
        7. Customer notification and verification workflow
        8. Integration with external fraud databases
        """
        
        result = await banking_orchestrator.handle_change_request(cr_description)
        
        cr_result = result['result']
        
        # Verify analysis identifies security pattern
        analysis = cr_result['analysis']
        assert 'fraud' in analysis['keywords'] or 'security' in analysis['keywords']
        assert analysis['priority'] == 'high'  # Security should be high priority
        
        # Verify implementation suggests comprehensive security measures
        implementation = cr_result['implementation']
        
        # Should include both Flutter and Python changes
        assert 'flutter_changes' in implementation
        assert 'python_changes' in implementation
        
        # Python changes should include ML and security services
        python_changes = implementation['python_changes']
        if 'new_services' in python_changes:
            services = python_changes['new_services']
            service_names = [str(service) for service in services]
            assert any('Fraud' in name or 'Security' in name or 'Risk' in name for name in service_names)
        
        # Should have high complexity due to ML integration
        effort = cr_result['estimated_effort']
        assert effort['complexity'] in ['medium', 'high']
        assert effort['total_days'] > 10  # Complex security feature
    
    @pytest.mark.asyncio
    async def test_loan_emi_calculator_scenario(self, banking_orchestrator):
        """Test loan EMI calculator enhancement scenario"""
        
        cr_description = """
        Enhance loan EMI calculator with:
        1. Multiple loan types (Personal, Home, Car, Education)
        2. Variable interest rate calculations
        3. Prepayment impact calculator
        4. Amortization schedule with charts
        5. Tax benefit calculator for home loans
        6. Comparison with other banks' rates
        7. Eligibility checker based on income and CIBIL score
        8. Direct loan application from calculator
        """
        
        result = await banking_orchestrator.handle_change_request(cr_description)
        
        cr_result = result['result']
        
        # Verify analysis
        analysis = cr_result['analysis']
        assert 'loan' in analysis['keywords'] or 'emi' in analysis['keywords']
        
        # Verify implementation includes calculator enhancements
        implementation = cr_result['implementation']
        
        # Flutter changes should include calculator UI
        flutter_changes = implementation.get('flutter_changes', {})
        if 'modified_screens' in flutter_changes:
            screens = flutter_changes['modified_screens']
            assert any('Calculator' in str(screen) or 'Loan' in str(screen) for screen in screens)
        
        # Python changes should include calculation services
        python_changes = implementation.get('python_changes', {})
        if 'new_services' in python_changes:
            services = python_changes['new_services']
            assert any('Calculator' in str(service) or 'Loan' in str(service) for service in services)
        
        # Should include test scenarios for calculations
        test_scenarios = cr_result['test_scenarios']
        test_descriptions = [test['description'] for test in test_scenarios]
        assert any('calculation' in desc.lower() or 'emi' in desc.lower() for desc in test_descriptions)
    
    @pytest.mark.asyncio
    async def test_digital_fixed_deposit_scenario(self, banking_orchestrator):
        """Test digital fixed deposit creation scenario"""
        
        cr_description = """
        Implement digital fixed deposit creation:
        1. Online FD booking with instant confirmation
        2. Flexible tenure selection (7 days to 10 years)
        3. Interest rate calculator with compounding options
        4. Auto-renewal settings
        5. Premature withdrawal calculator with penalty
        6. Digital FD certificate generation
        7. Interest payout options (monthly, quarterly, maturity)
        8. Nomination facility
        9. Integration with tax calculation for TDS
        """
        
        result = await banking_orchestrator.handle_change_request(cr_description)
        
        cr_result = result['result']
        
        # Verify analysis identifies investment pattern
        analysis = cr_result['analysis']
        assert any(keyword in analysis['keywords'] for keyword in ['fd', 'deposit', 'investment'])
        
        # Verify implementation includes FD-specific features
        implementation = cr_result['implementation']
        
        # Should suggest new screens for FD management
        flutter_changes = implementation.get('flutter_changes', {})
        if 'new_screens' in flutter_changes:
            screens = flutter_changes['new_screens']
            screen_names = [screen.get('name', '') for screen in screens]
            assert any('FD' in name or 'Deposit' in name for name in screen_names)
        
        # Should include compliance for banking regulations
        if 'compliance_requirements' in implementation:
            compliance = implementation['compliance_requirements']
            assert any('banking' in req.lower() or 'rbi' in req.lower() for req in compliance)
    
    @pytest.mark.asyncio
    async def test_bill_payment_integration_scenario(self, banking_orchestrator):
        """Test bill payment integration scenario"""
        
        cr_description = """
        Integrate comprehensive bill payment system:
        1. Electricity bill payment with all state boards
        2. Mobile and DTH recharge
        3. Gas bill payment
        4. Water bill payment
        5. Insurance premium payment
        6. Credit card bill payment
        7. Loan EMI payment
        8. Municipal tax payment
        9. BBPS (Bharat Bill Payment System) integration
        10. Bill reminder and auto-pay setup
        """
        
        result = await banking_orchestrator.handle_change_request(cr_description)
        
        cr_result = result['result']
        
        # Verify analysis
        analysis = cr_result['analysis']
        assert 'bill' in analysis['keywords'] or 'payment' in analysis['keywords']
        
        # Verify implementation includes BBPS integration
        implementation = cr_result['implementation']
        
        # Should mention BBPS compliance
        if 'compliance_requirements' in implementation:
            compliance = implementation['compliance_requirements']
            assert any('BBPS' in req for req in compliance)
        
        # Should include various bill types
        python_changes = implementation.get('python_changes', {})
        if 'new_endpoints' in python_changes:
            endpoints = python_changes['new_endpoints']
            endpoint_paths = [ep.get('path', '') for ep in endpoints]
            assert any('bill' in path.lower() for path in endpoint_paths)
    
    @pytest.mark.asyncio
    async def test_customer_support_chatbot_scenario(self, banking_orchestrator):
        """Test customer support chatbot integration scenario"""
        
        cr_description = """
        Implement AI-powered customer support chatbot:
        1. Natural language processing for customer queries
        2. Account balance and transaction inquiries
        3. Service request handling (checkbook, debit card)
        4. FAQ automation with banking-specific responses
        5. Escalation to human agents for complex issues
        6. Multi-language support (English, Hindi, Regional)
        7. Voice-to-text integration
        8. Integration with existing CRM system
        9. Sentiment analysis for customer satisfaction
        10. 24/7 availability with offline message handling
        """
        
        result = await banking_orchestrator.handle_change_request(cr_description)
        
        cr_result = result['result']
        
        # Verify analysis identifies AI/chatbot pattern
        analysis = cr_result['analysis']
        assert any(keyword in analysis['keywords'] for keyword in ['chatbot', 'ai', 'support', 'customer'])
        
        # Should be complex due to AI integration
        effort = cr_result['estimated_effort']
        assert effort['complexity'] in ['medium', 'high']
        
        # Should include both Flutter and Python components
        implementation = cr_result['implementation']
        assert 'flutter_changes' in implementation
        assert 'python_changes' in implementation
        
        # Should suggest AI/ML services
        python_changes = implementation.get('python_changes', {})
        if 'new_services' in python_changes:
            services = python_changes['new_services']
            service_names = [str(service) for service in services]
            assert any('AI' in name or 'NLP' in name or 'Chatbot' in name for name in service_names)
    
    @pytest.mark.asyncio
    async def test_regulatory_compliance_scenario(self, banking_orchestrator):
        """Test regulatory compliance enhancement scenario"""
        
        cr_description = """
        Enhance regulatory compliance features:
        1. AML (Anti-Money Laundering) transaction monitoring
        2. KYC periodic review and updates
        3. FATCA (Foreign Account Tax Compliance Act) reporting
        4. Suspicious transaction reporting (STR)
        5. Cash transaction reporting (CTR) for high-value transactions
        6. PEP (Politically Exposed Person) screening
        7. Sanctions list screening
        8. Audit trail maintenance for all transactions
        9. Regulatory reporting automation
        10. Data retention policy compliance
        """
        
        result = await banking_orchestrator.handle_change_request(cr_description)
        
        cr_result = result['result']
        
        # Verify analysis identifies compliance pattern
        analysis = cr_result['analysis']
        assert any(keyword in analysis['keywords'] for keyword in ['compliance', 'regulatory', 'aml', 'kyc'])
        assert analysis['priority'] == 'high'  # Compliance should be high priority
        
        # Should have high complexity due to regulatory requirements
        effort = cr_result['estimated_effort']
        assert effort['complexity'] == 'high'
        
        # Should include extensive compliance requirements
        implementation = cr_result['implementation']
        if 'compliance_requirements' in implementation:
            compliance = implementation['compliance_requirements']
            assert len(compliance) > 3  # Should have multiple compliance requirements
            assert any('AML' in req or 'KYC' in req or 'RBI' in req for req in compliance)
    
    @pytest.mark.asyncio
    async def test_cross_scenario_integration(self, banking_orchestrator):
        """Test integration across multiple banking scenarios"""
        
        # Process multiple related CRs
        cr1 = "Enhance KYC verification with biometric authentication"
        cr2 = "Implement transaction limits based on enhanced KYC levels"
        cr3 = "Add fraud detection for high-value transactions"
        
        result1 = await banking_orchestrator.handle_change_request(cr1)
        result2 = await banking_orchestrator.handle_change_request(cr2)
        result3 = await banking_orchestrator.handle_change_request(cr3)
        
        # Verify all CRs were processed
        assert all('cr_id' in result for result in [result1, result2, result3])
        
        # Verify memory agent stored all CRs
        assert banking_orchestrator.memory_agent.store_change_request.call_count == 3
        
        # Verify different patterns were identified
        patterns = [
            result1['result']['analysis']['pattern'],
            result2['result']['analysis']['pattern'],
            result3['result']['analysis']['pattern']
        ]
        
        # Should identify different but related patterns
        assert len(set(patterns)) >= 2  # At least 2 different patterns
        
        # All should be related to security/compliance
        security_keywords = ['biometric', 'kyc', 'fraud', 'security', 'authentication']
        for result in [result1, result2, result3]:
            analysis = result['result']['analysis']
            assert any(keyword in analysis['keywords'] for keyword in security_keywords)

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=agents', '--cov-report=html'])