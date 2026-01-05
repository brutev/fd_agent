import asyncio
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

from memory.vector_store import VectorStore
from memory.structured_store import StructuredStore

class CRHandlerAgent:
    """Agent that handles change requests and suggests implementations"""
    
    def __init__(self, vector_store: VectorStore, structured_store: StructuredStore):
        self.vector_store = vector_store
        self.structured_store = structured_store
        
        # CR patterns and their typical implementations
        self.cr_patterns = {
            'upi_autopay': {
                'keywords': ['upi', 'autopay', 'mandate', 'recurring'],
                'flutter_components': ['UPI', 'payment', 'mandate', 'recurring'],
                'python_components': ['upi', 'mandate', 'payment', 'recurring'],
                'implementation_type': 'feature_addition'
            },
            'biometric_auth': {
                'keywords': ['biometric', 'fingerprint', 'face', 'authentication'],
                'flutter_components': ['biometric', 'auth', 'fingerprint'],
                'python_components': ['auth', 'biometric', 'verification'],
                'implementation_type': 'security_enhancement'
            },
            'kyc_enhancement': {
                'keywords': ['kyc', 'aadhaar', 'offline', 'xml', 'verification'],
                'flutter_components': ['kyc', 'aadhaar', 'document'],
                'python_components': ['kyc', 'aadhaar', 'verification'],
                'implementation_type': 'compliance_update'
            },
            'transaction_limits': {
                'keywords': ['limit', 'transaction', 'kyc', 'based'],
                'flutter_components': ['transaction', 'limit', 'validation'],
                'python_components': ['transaction', 'limit', 'validation'],
                'implementation_type': 'business_rule'
            },
            'tax_statement': {
                'keywords': ['tax', 'statement', 'itr', 'tds', 'annual'],
                'flutter_components': ['statement', 'download', 'pdf'],
                'python_components': ['statement', 'tax', 'pdf', 'generation'],
                'implementation_type': 'reporting_feature'
            }
        }
    
    async def handle_change_request(self, cr_id: str, description: str) -> Dict[str, Any]:
        """Main method to handle a change request"""
        
        # Step 1: Analyze the CR description
        cr_analysis = self._analyze_cr_description(description)
        
        # Step 2: Retrieve relevant context
        context = await self._retrieve_relevant_context(description, cr_analysis)
        
        # Step 3: Generate implementation suggestions
        implementation = await self._generate_implementation_suggestions(cr_analysis, context)
        
        # Step 4: Identify affected components
        affected_components = await self._identify_affected_components(cr_analysis, context)
        
        # Step 5: Generate test scenarios
        test_scenarios = self._generate_test_scenarios(cr_analysis, implementation)
        
        return {
            'cr_id': cr_id,
            'analysis': cr_analysis,
            'context': context,
            'implementation': implementation,
            'affected_components': affected_components,
            'test_scenarios': test_scenarios,
            'estimated_effort': self._estimate_effort(implementation),
            'compliance_considerations': self._get_compliance_considerations(cr_analysis)
        }
    
    def _analyze_cr_description(self, description: str) -> Dict[str, Any]:
        """Analyze CR description to understand requirements"""
        description_lower = description.lower()
        
        # Identify CR pattern
        identified_pattern = None
        confidence = 0.0
        
        for pattern_name, pattern_info in self.cr_patterns.items():
            keyword_matches = sum(1 for keyword in pattern_info['keywords'] if keyword in description_lower)
            pattern_confidence = keyword_matches / len(pattern_info['keywords'])
            
            if pattern_confidence > confidence:
                confidence = pattern_confidence
                identified_pattern = pattern_name
        
        # Extract key entities
        entities = self._extract_entities(description)
        
        # Determine implementation scope
        scope = self._determine_scope(description)
        
        return {
            'pattern': identified_pattern,
            'confidence': confidence,
            'entities': entities,
            'scope': scope,
            'keywords': self._extract_keywords(description),
            'priority': self._determine_priority(description),
            'complexity': self._estimate_complexity(description)
        }
    
    async def _retrieve_relevant_context(self, description: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant code context for the CR"""
        
        # Search for relevant Flutter code
        flutter_context = self.vector_store.search_flutter_code(description, n_results=10)
        
        # Search for relevant Python code
        python_context = self.vector_store.search_python_code(description, n_results=10)
        
        # Search for similar CRs
        similar_crs = self.vector_store.search_similar_crs(description, n_results=5)
        
        # Get specific components based on pattern
        specific_context = await self._get_pattern_specific_context(analysis)
        
        return {
            'flutter_code': flutter_context,
            'python_code': python_context,
            'similar_crs': similar_crs,
            'specific_context': specific_context,
            'api_mappings': await self._get_relevant_api_mappings(analysis)
        }
    
    async def _generate_implementation_suggestions(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation suggestions based on analysis and context"""
        
        pattern = analysis.get('pattern')
        
        if pattern == 'upi_autopay':
            return await self._suggest_upi_autopay_implementation(context)
        elif pattern == 'biometric_auth':
            return await self._suggest_biometric_auth_implementation(context)
        elif pattern == 'kyc_enhancement':
            return await self._suggest_kyc_enhancement_implementation(context)
        elif pattern == 'transaction_limits':
            return await self._suggest_transaction_limits_implementation(context)
        elif pattern == 'tax_statement':
            return await self._suggest_tax_statement_implementation(context)
        else:
            return await self._suggest_generic_implementation(analysis, context)
    
    async def _suggest_upi_autopay_implementation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest implementation for UPI AutoPay feature"""
        
        return {
            'flutter_changes': {
                'new_screens': [
                    {
                        'name': 'UPIAutopaySetupPage',
                        'path': 'lib/features/transactions/presentation/pages/upi_autopay_setup_page.dart',
                        'description': 'Screen for setting up UPI AutoPay mandates',
                        'components': ['mandate form', 'amount limits', 'frequency selection', 'merchant details']
                    },
                    {
                        'name': 'MandateManagementPage',
                        'path': 'lib/features/transactions/presentation/pages/mandate_management_page.dart',
                        'description': 'Screen for managing existing mandates',
                        'components': ['mandate list', 'pause/resume', 'modify limits', 'cancel mandate']
                    }
                ],
                'modified_screens': [
                    {
                        'name': 'UPIPaymentPage',
                        'path': 'lib/features/transactions/presentation/pages/upi_payment_page.dart',
                        'changes': ['Add AutoPay option', 'Mandate setup flow integration']
                    }
                ],
                'new_widgets': [
                    'MandateCard',
                    'AutoPayToggle',
                    'FrequencySelector',
                    'AmountLimitInput'
                ],
                'bloc_changes': [
                    {
                        'name': 'UPIPaymentBloc',
                        'new_events': ['SetupMandateEvent', 'ModifyMandateEvent', 'CancelMandateEvent'],
                        'new_states': ['MandateSetupState', 'MandateActiveState', 'MandateErrorState']
                    }
                ]
            },
            'python_changes': {
                'new_endpoints': [
                    {
                        'path': '/api/v1/upi/mandate/create',
                        'method': 'POST',
                        'description': 'Create UPI AutoPay mandate',
                        'parameters': ['merchant_id', 'amount_limit', 'frequency', 'start_date', 'end_date']
                    },
                    {
                        'path': '/api/v1/upi/mandate/{mandate_id}',
                        'method': 'GET',
                        'description': 'Get mandate details'
                    },
                    {
                        'path': '/api/v1/upi/mandate/{mandate_id}/modify',
                        'method': 'PUT',
                        'description': 'Modify existing mandate'
                    },
                    {
                        'path': '/api/v1/upi/mandate/{mandate_id}/cancel',
                        'method': 'DELETE',
                        'description': 'Cancel mandate'
                    }
                ],
                'new_models': [
                    {
                        'name': 'UPIMandateRequest',
                        'fields': ['merchant_id', 'amount_limit', 'frequency', 'start_date', 'end_date']
                    },
                    {
                        'name': 'UPIMandateResponse',
                        'fields': ['mandate_id', 'status', 'created_at', 'next_debit_date']
                    }
                ],
                'database_changes': [
                    {
                        'table': 'upi_mandates',
                        'columns': ['id', 'user_id', 'merchant_id', 'amount_limit', 'frequency', 'status', 'created_at', 'updated_at']
                    }
                ],
                'business_logic': [
                    'Mandate validation (NPCI compliance)',
                    'Automatic debit processing',
                    'Failure handling and retry logic',
                    'Notification system for mandate events'
                ]
            },
            'compliance_requirements': [
                'NPCI AutoPay guidelines compliance',
                'Customer consent management',
                'Mandate registration with NPCI',
                'Transaction limit validation'
            ]
        }
    
    async def _suggest_biometric_auth_implementation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest implementation for biometric authentication"""
        
        return {
            'flutter_changes': {
                'dependencies': ['local_auth: ^2.1.6'],
                'modified_screens': [
                    {
                        'name': 'LoginPage',
                        'changes': ['Add biometric login option', 'Fallback to MPIN']
                    },
                    {
                        'name': 'TransactionConfirmationPage',
                        'changes': ['Biometric verification for high-value transactions']
                    }
                ],
                'new_services': [
                    {
                        'name': 'BiometricAuthService',
                        'methods': ['checkBiometricSupport', 'authenticateWithBiometric', 'enableBiometric']
                    }
                ],
                'bloc_changes': [
                    {
                        'name': 'AuthBloc',
                        'new_events': ['BiometricLoginEvent', 'EnableBiometricEvent'],
                        'new_states': ['BiometricAuthenticatedState', 'BiometricFailedState']
                    }
                ]
            },
            'python_changes': {
                'new_endpoints': [
                    {
                        'path': '/api/v1/auth/biometric/enable',
                        'method': 'POST',
                        'description': 'Enable biometric authentication for user'
                    },
                    {
                        'path': '/api/v1/auth/biometric/verify',
                        'method': 'POST',
                        'description': 'Verify biometric authentication'
                    }
                ],
                'database_changes': [
                    {
                        'table': 'users',
                        'new_columns': ['biometric_enabled', 'biometric_public_key']
                    }
                ],
                'security_enhancements': [
                    'Biometric template storage (encrypted)',
                    'Device binding for biometric auth',
                    'Fallback mechanism to MPIN'
                ]
            }
        }
    
    async def _suggest_kyc_enhancement_implementation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest implementation for KYC enhancement"""
        
        return {
            'flutter_changes': {
                'new_screens': [
                    {
                        'name': 'OfflineKYCPage',
                        'description': 'Screen for offline Aadhaar KYC using XML file',
                        'components': ['file picker', 'XML parser', 'signature verification']
                    }
                ],
                'dependencies': ['file_picker: ^5.2.5', 'xml: ^6.2.2'],
                'new_services': [
                    {
                        'name': 'AadhaarXMLParser',
                        'methods': ['parseXMLFile', 'verifySignature', 'extractDemographics']
                    }
                ]
            },
            'python_changes': {
                'new_endpoints': [
                    {
                        'path': '/api/v1/kyc/aadhaar/offline',
                        'method': 'POST',
                        'description': 'Process offline Aadhaar KYC XML'
                    }
                ],
                'new_services': [
                    'AadhaarXMLValidator',
                    'DigitalSignatureVerifier',
                    'DemographicDataExtractor'
                ],
                'compliance_requirements': [
                    'UIDAI offline KYC guidelines',
                    'XML signature verification',
                    'Data privacy compliance'
                ]
            }
        }
    
    async def _suggest_transaction_limits_implementation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest implementation for transaction limits based on KYC"""
        
        return {
            'flutter_changes': {
                'modified_screens': [
                    {
                        'name': 'TransactionPages',
                        'changes': ['Display applicable limits', 'Limit validation', 'KYC upgrade prompts']
                    }
                ],
                'new_widgets': [
                    'LimitDisplayWidget',
                    'KYCUpgradePrompt'
                ]
            },
            'python_changes': {
                'modified_endpoints': [
                    {
                        'endpoints': ['NEFT', 'RTGS', 'IMPS', 'UPI'],
                        'changes': ['Add KYC-based limit validation']
                    }
                ],
                'new_services': [
                    'TransactionLimitService',
                    'KYCLevelValidator'
                ],
                'business_rules': [
                    'Minimum KYC: ₹10,000/day',
                    'Full KYC: ₹1,00,000/day',
                    'Enhanced KYC: ₹10,00,000/day'
                ]
            }
        }
    
    async def _suggest_tax_statement_implementation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest implementation for tax statement generation"""
        
        return {
            'flutter_changes': {
                'new_screens': [
                    {
                        'name': 'TaxStatementPage',
                        'description': 'Screen for generating and downloading tax statements',
                        'components': ['year selector', 'statement type', 'download options']
                    }
                ]
            },
            'python_changes': {
                'new_endpoints': [
                    {
                        'path': '/api/v1/statements/tax/{year}',
                        'method': 'GET',
                        'description': 'Generate annual tax statement'
                    }
                ],
                'new_services': [
                    'TaxCalculationService',
                    'Form26ASGenerator',
                    'TDSCalculator'
                ],
                'compliance_requirements': [
                    'Income Tax Act compliance',
                    'TDS/TCS calculation accuracy',
                    'Form 26AS format adherence'
                ]
            }
        }
    
    async def _suggest_generic_implementation(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest generic implementation based on analysis"""
        
        return {
            'analysis_based_suggestions': {
                'scope': analysis.get('scope'),
                'complexity': analysis.get('complexity'),
                'entities': analysis.get('entities'),
                'similar_implementations': [item['metadata'] for item in context.get('similar_crs', [])]
            },
            'recommended_approach': 'Analyze similar implementations and adapt patterns',
            'next_steps': [
                'Gather more specific requirements',
                'Review similar change requests',
                'Consult domain experts',
                'Create detailed technical specification'
            ]
        }
    
    async def _identify_affected_components(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify components that will be affected by the CR"""
        
        affected = {
            'flutter_components': [],
            'python_components': [],
            'database_changes': [],
            'external_integrations': [],
            'test_files': []
        }
        
        # Analyze context to identify affected components
        for flutter_item in context.get('flutter_code', []):
            metadata = flutter_item.get('metadata', {})
            if any(keyword in str(metadata).lower() for keyword in analysis.get('keywords', [])):
                affected['flutter_components'].append({
                    'file': metadata.get('file_path'),
                    'component': metadata.get('name'),
                    'type': metadata.get('type')
                })
        
        for python_item in context.get('python_code', []):
            metadata = python_item.get('metadata', {})
            if any(keyword in str(metadata).lower() for keyword in analysis.get('keywords', [])):
                affected['python_components'].append({
                    'file': metadata.get('file_path'),
                    'component': metadata.get('name'),
                    'type': metadata.get('type')
                })
        
        return affected
    
    def _generate_test_scenarios(self, analysis: Dict[str, Any], implementation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test scenarios for the CR implementation"""
        
        scenarios = []
        pattern = analysis.get('pattern')
        
        if pattern == 'upi_autopay':
            scenarios.extend([
                {
                    'type': 'unit_test',
                    'description': 'Test mandate creation with valid parameters',
                    'test_file': 'test/unit/features/transactions/test_upi_autopay.dart'
                },
                {
                    'type': 'widget_test',
                    'description': 'Test UPI AutoPay setup page UI',
                    'test_file': 'test/widget/transactions/upi_autopay_setup_test.dart'
                },
                {
                    'type': 'integration_test',
                    'description': 'Test complete mandate setup flow',
                    'test_file': 'test/integration/upi_autopay_flow_test.dart'
                },
                {
                    'type': 'api_test',
                    'description': 'Test mandate creation API endpoint',
                    'test_file': 'backend/tests/unit/test_api_endpoints/test_upi_mandate.py'
                }
            ])
        elif pattern == 'biometric_auth':
            scenarios.extend([
                {
                    'type': 'unit_test',
                    'description': 'Test biometric authentication service',
                    'test_file': 'test/unit/core/services/test_biometric_auth_service.dart'
                },
                {
                    'type': 'widget_test',
                    'description': 'Test biometric login UI',
                    'test_file': 'test/widget/auth/biometric_login_test.dart'
                },
                {
                    'type': 'security_test',
                    'description': 'Test biometric fallback mechanisms',
                    'test_file': 'test/security/biometric_security_test.dart'
                }
            ])
        
        # Add common test scenarios
        scenarios.extend([
            {
                'type': 'error_handling',
                'description': 'Test error scenarios and edge cases',
                'priority': 'high'
            },
            {
                'type': 'performance',
                'description': 'Test performance impact of changes',
                'priority': 'medium'
            },
            {
                'type': 'regression',
                'description': 'Test existing functionality is not broken',
                'priority': 'high'
            }
        ])
        
        return scenarios
    
    def _estimate_effort(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate development effort for the implementation"""
        
        flutter_changes = implementation.get('flutter_changes', {})
        python_changes = implementation.get('python_changes', {})
        
        # Simple effort estimation based on number of changes
        flutter_effort = (
            len(flutter_changes.get('new_screens', [])) * 2 +
            len(flutter_changes.get('modified_screens', [])) * 1 +
            len(flutter_changes.get('new_widgets', [])) * 0.5 +
            len(flutter_changes.get('bloc_changes', [])) * 1.5
        )
        
        python_effort = (
            len(python_changes.get('new_endpoints', [])) * 1.5 +
            len(python_changes.get('new_models', [])) * 0.5 +
            len(python_changes.get('new_services', [])) * 2 +
            len(python_changes.get('database_changes', [])) * 1
        )
        
        total_effort = flutter_effort + python_effort
        
        return {
            'flutter_days': flutter_effort,
            'python_days': python_effort,
            'total_days': total_effort,
            'complexity': 'low' if total_effort < 5 else 'medium' if total_effort < 15 else 'high',
            'team_size': 1 if total_effort < 10 else 2 if total_effort < 20 else 3
        }
    
    def _get_compliance_considerations(self, analysis: Dict[str, Any]) -> List[str]:
        """Get compliance considerations for the CR"""
        
        pattern = analysis.get('pattern')
        
        compliance_map = {
            'upi_autopay': [
                'NPCI AutoPay guidelines compliance',
                'RBI guidelines for recurring payments',
                'Customer consent management',
                'Data privacy regulations'
            ],
            'biometric_auth': [
                'Biometric data protection laws',
                'Device security standards',
                'Authentication fallback requirements',
                'Privacy policy updates'
            ],
            'kyc_enhancement': [
                'UIDAI guidelines for offline KYC',
                'KYC data storage regulations',
                'Customer data privacy',
                'Audit trail requirements'
            ],
            'transaction_limits': [
                'RBI KYC guidelines',
                'AML compliance',
                'Transaction monitoring',
                'Customer notification requirements'
            ],
            'tax_statement': [
                'Income Tax Act compliance',
                'TDS/TCS calculation accuracy',
                'Data retention policies',
                'Customer data privacy'
            ]
        }
        
        return compliance_map.get(pattern, [
            'General banking regulations',
            'Data privacy compliance',
            'Security standards',
            'Audit requirements'
        ])
    
    def _extract_entities(self, description: str) -> List[str]:
        """Extract key entities from CR description"""
        entities = []
        
        # Common banking entities
        banking_entities = [
            'account', 'transaction', 'payment', 'transfer', 'balance',
            'kyc', 'aadhaar', 'pan', 'upi', 'neft', 'rtgs', 'imps',
            'loan', 'emi', 'interest', 'statement', 'receipt'
        ]
        
        description_lower = description.lower()
        for entity in banking_entities:
            if entity in description_lower:
                entities.append(entity)
        
        return entities
    
    def _determine_scope(self, description: str) -> str:
        """Determine the scope of the CR"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['new', 'add', 'create', 'implement']):
            return 'feature_addition'
        elif any(word in description_lower for word in ['modify', 'update', 'change', 'enhance']):
            return 'feature_modification'
        elif any(word in description_lower for word in ['fix', 'bug', 'issue', 'error']):
            return 'bug_fix'
        elif any(word in description_lower for word in ['security', 'compliance', 'regulation']):
            return 'compliance_update'
        else:
            return 'general_enhancement'
    
    def _extract_keywords(self, description: str) -> List[str]:
        """Extract keywords from CR description"""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', description.lower())
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return list(set(keywords))
    
    def _determine_priority(self, description: str) -> str:
        """Determine priority of the CR"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['urgent', 'critical', 'asap', 'immediately']):
            return 'high'
        elif any(word in description_lower for word in ['compliance', 'security', 'regulation']):
            return 'high'
        elif any(word in description_lower for word in ['enhancement', 'improvement', 'optimize']):
            return 'medium'
        else:
            return 'low'
    
    def _estimate_complexity(self, description: str) -> str:
        """Estimate complexity of the CR"""
        description_lower = description.lower()
        
        complexity_indicators = {
            'high': ['integration', 'compliance', 'security', 'migration', 'architecture'],
            'medium': ['enhancement', 'modification', 'validation', 'calculation'],
            'low': ['display', 'ui', 'text', 'color', 'layout']
        }
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return complexity
        
        return 'medium'
    
    async def _get_pattern_specific_context(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get context specific to the identified pattern"""
        pattern = analysis.get('pattern')
        
        if not pattern:
            return {}
        
        pattern_info = self.cr_patterns.get(pattern, {})
        
        # Search for Flutter components
        flutter_context = []
        for component in pattern_info.get('flutter_components', []):
            results = self.vector_store.search_flutter_code(component, n_results=3)
            flutter_context.extend(results)
        
        # Search for Python components
        python_context = []
        for component in pattern_info.get('python_components', []):
            results = self.vector_store.search_python_code(component, n_results=3)
            python_context.extend(results)
        
        return {
            'flutter_components': flutter_context,
            'python_components': python_context,
            'implementation_type': pattern_info.get('implementation_type')
        }
    
    async def _get_relevant_api_mappings(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get relevant API mappings for the CR"""
        # This would query the structured store for API mappings
        # For now, return empty list
        return []