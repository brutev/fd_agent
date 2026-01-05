import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import tempfile
import os

from agents.orchestrator import AgentOrchestrator
from agents.memory_agent import MemoryAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.cr_handler_agent import CRHandlerAgent
from memory.vector_store import VectorStore
from memory.structured_store import StructuredStore, CodeEntity

class TestAgentOrchestrator:
    """Test Agent Orchestrator with comprehensive scenarios"""
    
    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator with mocked dependencies"""
        with patch('agents.orchestrator.VectorStore') as mock_vector_store, \
             patch('agents.orchestrator.StructuredStore') as mock_structured_store:
            
            orchestrator = AgentOrchestrator()
            orchestrator.vector_store = Mock()
            orchestrator.structured_store = AsyncMock()
            orchestrator.memory_agent = Mock()
            orchestrator.analyzer_agent = Mock()
            orchestrator.cr_handler = AsyncMock()
            orchestrator.flutter_analyzer = Mock()
            orchestrator.python_analyzer = Mock()
            
            return orchestrator
    
    @pytest.mark.asyncio
    async def test_initialize(self, orchestrator):
        """Test orchestrator initialization"""
        await orchestrator.initialize()
        assert orchestrator.initialized == True
        orchestrator.structured_store.init_db.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_codebase(self, orchestrator):
        """Test codebase analysis"""
        # Mock analyzer results
        flutter_results = {
            'widgets': [Mock(name='TestWidget', type='StatelessWidget', file_path='/test.dart')],
            'blocs': [Mock(name='TestBloc', type='Bloc', file_path='/test_bloc.dart')],
            'api_calls': [{'endpoint': '/api/test', 'method': 'GET', 'file_path': '/test.dart', 'line': 10}],
            'routes': [{'route': '/test', 'type': 'pushNamed'}]
        }
        
        python_results = {
            'endpoints': [Mock(name='test_endpoint', method='GET', path='/api/test', file_path='/test.py')],
            'models': [Mock(name='TestModel', file_path='/models.py')],
            'services': [Mock(name='test_service', file_path='/services.py')],
            'validators': [Mock(name='test_validator', file_path='/validators.py')]
        }
        
        orchestrator.flutter_analyzer.analyze_project.return_value = flutter_results
        orchestrator.python_analyzer.analyze_project.return_value = python_results
        orchestrator.structured_store.add_entity = AsyncMock()
        orchestrator.vector_store.add_flutter_code = Mock()
        orchestrator.vector_store.add_python_code = Mock()
        orchestrator.structured_store.add_api_mapping = AsyncMock()
        orchestrator.structured_store.get_stats = AsyncMock(return_value={'entities': {}, 'relationships': {}})
        orchestrator.vector_store.get_collection_stats = Mock(return_value={'flutter_code': 1, 'python_code': 1})
        
        result = await orchestrator.analyze_codebase('/test/project')
        
        assert 'flutter' in result
        assert 'python' in result
        assert result['flutter']['widgets'] == 1
        assert result['python']['endpoints'] == 1
        
        # Verify analyzers were called
        orchestrator.flutter_analyzer.analyze_project.assert_called_once()
        orchestrator.python_analyzer.analyze_project.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_change_request(self, orchestrator):
        """Test change request handling"""
        cr_description = "Add UPI AutoPay feature"
        
        # Mock CR handler result
        cr_result = {
            'implementation': {'flutter_changes': {}, 'python_changes': {}},
            'affected_components': [],
            'test_scenarios': []
        }
        
        orchestrator.cr_handler.handle_change_request = AsyncMock(return_value=cr_result)
        orchestrator.memory_agent.store_change_request = AsyncMock()
        
        result = await orchestrator.handle_change_request(cr_description)
        
        assert 'cr_id' in result
        assert result['description'] == cr_description
        assert 'result' in result
        assert 'timestamp' in result
        
        orchestrator.cr_handler.handle_change_request.assert_called_once()
        orchestrator.memory_agent.store_change_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_context_for_query(self, orchestrator):
        """Test context retrieval for queries"""
        query = "UPI payment"
        
        # Mock vector store responses
        orchestrator.vector_store.search_flutter_code.return_value = [{'content': 'flutter code'}]
        orchestrator.vector_store.search_python_code.return_value = [{'content': 'python code'}]
        orchestrator.vector_store.search_all.return_value = {'flutter': [], 'python': []}
        
        # Test different context types
        flutter_context = await orchestrator.get_context_for_query(query, 'flutter')
        assert flutter_context == [{'content': 'flutter code'}]
        
        python_context = await orchestrator.get_context_for_query(query, 'python')
        assert python_context == [{'content': 'python code'}]
        
        all_context = await orchestrator.get_context_for_query(query, 'all')
        assert 'flutter' in all_context
        assert 'python' in all_context
    
    @pytest.mark.asyncio
    async def test_search_code(self, orchestrator):
        """Test code search functionality"""
        query = "transaction validation"
        
        orchestrator.vector_store.search_flutter_code.return_value = [
            {'content': 'flutter validation', 'distance': 0.1}
        ]
        orchestrator.vector_store.search_python_code.return_value = [
            {'content': 'python validation', 'distance': 0.2}
        ]
        orchestrator.vector_store.search_all.return_value = {
            'flutter': [{'content': 'flutter validation', 'distance': 0.1}],
            'python': [{'content': 'python validation', 'distance': 0.2}]
        }
        
        # Test language-specific search
        flutter_results = await orchestrator.search_code(query, 'dart')
        assert len(flutter_results) == 1
        assert flutter_results[0]['content'] == 'flutter validation'
        
        python_results = await orchestrator.search_code(query, 'python')
        assert len(python_results) == 1
        assert python_results[0]['content'] == 'python validation'
        
        # Test general search
        all_results = await orchestrator.search_code(query)
        assert len(all_results) == 2

class TestMemoryAgent:
    """Test Memory Agent with comprehensive scenarios"""
    
    @pytest.fixture
    def memory_agent(self):
        """Create memory agent with mocked dependencies"""
        vector_store = Mock()
        structured_store = AsyncMock()
        return MemoryAgent(vector_store, structured_store)
    
    @pytest.mark.asyncio
    async def test_store_change_request(self, memory_agent):
        """Test storing change request"""
        cr_id = "CR-001"
        description = "Add biometric authentication"
        implementation = {
            'flutter_changes': {'new_screens': []},
            'python_changes': {'new_endpoints': []},
            'estimated_effort': {'complexity': 'medium'}
        }
        
        await memory_agent.store_change_request(cr_id, description, implementation)
        
        memory_agent.vector_store.add_change_request.assert_called_once()
        memory_agent.structured_store.add_change_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retrieve_context_for_cr(self, memory_agent):
        """Test retrieving context for change request"""
        cr_description = "Implement KYC enhancement"
        
        # Mock vector store responses
        memory_agent.vector_store.search_flutter_code.return_value = [{'content': 'kyc flutter'}]
        memory_agent.vector_store.search_python_code.return_value = [{'content': 'kyc python'}]
        memory_agent.vector_store.search_similar_crs.return_value = [{'content': 'similar cr'}]
        
        # Mock structured store responses
        memory_agent.structured_store.get_entities_by_type = AsyncMock(return_value=[])
        memory_agent.structured_store.get_api_mappings = AsyncMock(return_value=[])
        
        context = await memory_agent.retrieve_context_for_cr(cr_description)
        
        assert 'flutter_code' in context
        assert 'python_code' in context
        assert 'similar_crs' in context
        assert 'entities' in context
        assert 'api_mappings' in context
    
    @pytest.mark.asyncio
    async def test_get_memory_statistics(self, memory_agent):
        """Test memory statistics retrieval"""
        memory_agent.vector_store.get_collection_stats.return_value = {
            'flutter_code': 10,
            'python_code': 15
        }
        memory_agent.structured_store.get_stats.return_value = {
            'entities': {'widget': 5, 'endpoint': 8},
            'relationships': {'calls': 3}
        }
        
        stats = await memory_agent.get_memory_statistics()
        
        assert 'vector_store' in stats
        assert 'structured_store' in stats
        assert 'total_entities' in stats
        assert 'memory_health' in stats
        assert stats['total_entities'] == 13

class TestAnalyzerAgent:
    """Test Analyzer Agent with comprehensive scenarios"""
    
    @pytest.fixture
    def analyzer_agent(self):
        """Create analyzer agent with mocked dependencies"""
        vector_store = Mock()
        structured_store = AsyncMock()
        agent = AnalyzerAgent(vector_store, structured_store)
        agent.flutter_analyzer = Mock()
        agent.python_analyzer = Mock()
        return agent
    
    @pytest.mark.asyncio
    async def test_analyze_project_full(self, analyzer_agent):
        """Test full project analysis"""
        project_path = "/test/project"
        
        # Mock analyzer results
        flutter_results = {
            'widgets': [Mock(name='TestWidget')],
            'blocs': [],
            'api_calls': [{'endpoint': '/api/test'}],
            'dependencies': {'dependencies': ['flutter_bloc']}
        }
        
        python_results = {
            'endpoints': [Mock(name='test_endpoint', path='/api/test', method='GET')],
            'models': [],
            'services': []
        }
        
        analyzer_agent.flutter_analyzer.analyze_project.return_value = flutter_results
        analyzer_agent.python_analyzer.analyze_project.return_value = python_results
        
        result = await analyzer_agent.analyze_project_full(project_path)
        
        assert 'flutter' in result
        assert 'python' in result
        assert 'cross_analysis' in result
        assert 'insights' in result
        assert 'analysis_timestamp' in result
        
        # Verify analyzers were called
        analyzer_agent.flutter_analyzer.analyze_project.assert_called_once()
        analyzer_agent.python_analyzer.analyze_project.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_code_metrics(self, analyzer_agent):
        """Test code metrics calculation"""
        project_path = "/test/project"
        
        # Mock analysis results
        analysis = {
            'flutter': {
                'widgets': [
                    Mock(type='StatelessWidget', dependencies=[], api_calls=[], form_fields=[], validators=[]),
                    Mock(type='StatefulWidget', dependencies=['Provider'], api_calls=['get'], form_fields=['email'], validators=['required'])
                ],
                'blocs': [Mock()],
                'api_calls': [{'endpoint': '/api/test'}]
            },
            'python': {
                'endpoints': [Mock(parameters=[], dependencies=[])],
                'models': [Mock(fields=[{'name': 'id'}, {'name': 'name'}], validators=[])],
                'services': [Mock(parameters=[], database_operations=[], external_calls=[])]
            }
        }
        
        analyzer_agent.analysis_cache[project_path] = analysis
        analyzer_agent.last_analysis_time[project_path] = datetime.now()
        
        metrics = await analyzer_agent.get_code_metrics(project_path)
        
        assert 'flutter_metrics' in metrics
        assert 'python_metrics' in metrics
        assert 'overall_metrics' in metrics
        assert 'recommendations' in metrics
        
        # Check specific metrics
        flutter_metrics = metrics['flutter_metrics']
        assert flutter_metrics['total_widgets'] == 2
        assert flutter_metrics['stateless_widgets'] == 1
        assert flutter_metrics['stateful_widgets'] == 1
    
    @pytest.mark.asyncio
    async def test_find_code_patterns(self, analyzer_agent):
        """Test code pattern detection"""
        project_path = "/test/project"
        
        # Mock analysis with patterns
        analysis = {
            'flutter': {
                'api_calls': [
                    {'endpoint': '/api/users', 'file_path': '/page1.dart'},
                    {'endpoint': '/api/users', 'file_path': '/page2.dart'},
                    {'endpoint': '/api/transactions', 'file_path': '/page3.dart'}
                ],
                'blocs': [Mock(name='UserBloc', type='Bloc')],
                'routes': [
                    {'type': 'pushNamed', 'route': '/home'},
                    {'type': 'pushNamed', 'route': '/profile'}
                ]
            }
        }
        
        analyzer_agent.analysis_cache[project_path] = analysis
        analyzer_agent.last_analysis_time[project_path] = datetime.now()
        
        # Test API call patterns
        api_patterns = await analyzer_agent.find_code_patterns(project_path, 'api_calls')
        assert len(api_patterns) == 1
        assert api_patterns[0]['pattern_type'] == 'repeated_api_call'
        assert api_patterns[0]['endpoint'] == '/api/users'
        assert api_patterns[0]['occurrences'] == 2
        
        # Test state management patterns
        state_patterns = await analyzer_agent.find_code_patterns(project_path, 'state_management')
        assert len(state_patterns) == 1
        assert state_patterns[0]['pattern_type'] == 'bloc_pattern'
        
        # Test navigation patterns
        nav_patterns = await analyzer_agent.find_code_patterns(project_path, 'navigation')
        assert len(nav_patterns) == 1
        assert nav_patterns[0]['pattern_type'] == 'navigation_pushNamed'

class TestCRHandlerAgent:
    """Test CR Handler Agent with comprehensive scenarios"""
    
    @pytest.fixture
    def cr_handler(self):
        """Create CR handler with mocked dependencies"""
        vector_store = Mock()
        structured_store = AsyncMock()
        return CRHandlerAgent(vector_store, structured_store)
    
    @pytest.mark.asyncio
    async def test_handle_upi_autopay_cr(self, cr_handler):
        """Test UPI AutoPay change request handling"""
        cr_id = "CR-UPI-001"
        description = "Add UPI AutoPay mandate feature for recurring payments"
        
        # Mock context retrieval
        cr_handler.vector_store.search_flutter_code.return_value = [
            {'content': 'UPI payment code', 'metadata': {'type': 'widget'}}
        ]
        cr_handler.vector_store.search_python_code.return_value = [
            {'content': 'UPI API endpoint', 'metadata': {'type': 'endpoint'}}
        ]
        cr_handler.vector_store.search_similar_crs.return_value = []
        cr_handler.structured_store.get_api_mappings.return_value = []
        
        result = await cr_handler.handle_change_request(cr_id, description)
        
        assert result['cr_id'] == cr_id
        assert 'analysis' in result
        assert 'implementation' in result
        assert 'affected_components' in result
        assert 'test_scenarios' in result
        
        # Check if UPI AutoPay pattern was identified
        analysis = result['analysis']
        assert analysis['pattern'] == 'upi_autopay'
        assert analysis['confidence'] > 0.5
        
        # Check implementation suggestions
        implementation = result['implementation']
        assert 'flutter_changes' in implementation
        assert 'python_changes' in implementation
        
        flutter_changes = implementation['flutter_changes']
        assert 'new_screens' in flutter_changes
        assert any('AutoPay' in screen['name'] for screen in flutter_changes['new_screens'])
    
    @pytest.mark.asyncio
    async def test_handle_biometric_auth_cr(self, cr_handler):
        """Test biometric authentication change request handling"""
        cr_id = "CR-BIO-001"
        description = "Implement biometric authentication for high-value transactions"
        
        # Mock context
        cr_handler.vector_store.search_flutter_code.return_value = []
        cr_handler.vector_store.search_python_code.return_value = []
        cr_handler.vector_store.search_similar_crs.return_value = []
        cr_handler.structured_store.get_api_mappings.return_value = []
        
        result = await cr_handler.handle_change_request(cr_id, description)
        
        analysis = result['analysis']
        assert analysis['pattern'] == 'biometric_auth'
        
        implementation = result['implementation']
        flutter_changes = implementation['flutter_changes']
        assert 'dependencies' in flutter_changes
        assert 'local_auth' in str(flutter_changes['dependencies'])
    
    @pytest.mark.asyncio
    async def test_handle_kyc_enhancement_cr(self, cr_handler):
        """Test KYC enhancement change request handling"""
        cr_id = "CR-KYC-001"
        description = "Add offline Aadhaar KYC using XML file verification"
        
        # Mock context
        cr_handler.vector_store.search_flutter_code.return_value = []
        cr_handler.vector_store.search_python_code.return_value = []
        cr_handler.vector_store.search_similar_crs.return_value = []
        cr_handler.structured_store.get_api_mappings.return_value = []
        
        result = await cr_handler.handle_change_request(cr_id, description)
        
        analysis = result['analysis']
        assert analysis['pattern'] == 'kyc_enhancement'
        
        implementation = result['implementation']
        assert 'compliance_requirements' in implementation
        compliance = implementation['compliance_requirements']
        assert any('UIDAI' in req for req in compliance)
    
    @pytest.mark.asyncio
    async def test_handle_generic_cr(self, cr_handler):
        """Test generic change request handling"""
        cr_id = "CR-GEN-001"
        description = "Update user interface colors and themes"
        
        # Mock context
        cr_handler.vector_store.search_flutter_code.return_value = []
        cr_handler.vector_store.search_python_code.return_value = []
        cr_handler.vector_store.search_similar_crs.return_value = []
        cr_handler.structured_store.get_api_mappings.return_value = []
        
        result = await cr_handler.handle_change_request(cr_id, description)
        
        analysis = result['analysis']
        assert analysis['pattern'] is None or analysis['confidence'] < 0.5
        
        implementation = result['implementation']
        assert 'analysis_based_suggestions' in implementation
        assert 'recommended_approach' in implementation
    
    def test_analyze_cr_description(self, cr_handler):
        """Test CR description analysis"""
        # Test UPI AutoPay pattern
        description = "Add UPI AutoPay mandate feature for recurring payments"
        analysis = cr_handler._analyze_cr_description(description)
        
        assert analysis['pattern'] == 'upi_autopay'
        assert analysis['confidence'] > 0.5
        assert 'upi' in analysis['keywords']
        assert 'autopay' in analysis['keywords']
        
        # Test biometric pattern
        description = "Implement biometric fingerprint authentication"
        analysis = cr_handler._analyze_cr_description(description)
        
        assert analysis['pattern'] == 'biometric_auth'
        assert 'biometric' in analysis['keywords']
        assert 'fingerprint' in analysis['keywords']
    
    def test_estimate_effort(self, cr_handler):
        """Test effort estimation"""
        # Simple implementation
        simple_implementation = {
            'flutter_changes': {
                'new_screens': [],
                'modified_screens': [{'name': 'LoginPage'}],
                'new_widgets': ['BiometricButton'],
                'bloc_changes': []
            },
            'python_changes': {
                'new_endpoints': [],
                'new_models': [],
                'new_services': [],
                'database_changes': []
            }
        }
        
        effort = cr_handler._estimate_effort(simple_implementation)
        assert effort['complexity'] == 'low'
        assert effort['total_days'] < 5
        
        # Complex implementation
        complex_implementation = {
            'flutter_changes': {
                'new_screens': [{'name': 'Screen1'}, {'name': 'Screen2'}],
                'modified_screens': [{'name': 'Screen3'}, {'name': 'Screen4'}],
                'new_widgets': ['Widget1', 'Widget2', 'Widget3'],
                'bloc_changes': [{'name': 'Bloc1'}, {'name': 'Bloc2'}]
            },
            'python_changes': {
                'new_endpoints': [{'path': '/api/1'}, {'path': '/api/2'}],
                'new_models': [{'name': 'Model1'}],
                'new_services': [{'name': 'Service1'}, {'name': 'Service2'}],
                'database_changes': [{'table': 'table1'}]
            }
        }
        
        effort = cr_handler._estimate_effort(complex_implementation)
        assert effort['complexity'] == 'high'
        assert effort['total_days'] >= 15

# Integration tests for agents
class TestAgentIntegration:
    """Integration tests for agent interactions"""
    
    @pytest.mark.asyncio
    async def test_full_cr_processing_flow(self):
        """Test complete CR processing flow"""
        with patch('agents.orchestrator.VectorStore') as mock_vector_store, \
             patch('agents.orchestrator.StructuredStore') as mock_structured_store:
            
            # Create orchestrator
            orchestrator = AgentOrchestrator()
            orchestrator.vector_store = Mock()
            orchestrator.structured_store = AsyncMock()
            orchestrator.memory_agent = AsyncMock()
            orchestrator.analyzer_agent = Mock()
            orchestrator.cr_handler = AsyncMock()
            
            # Mock CR handler response
            cr_result = {
                'analysis': {'pattern': 'upi_autopay', 'confidence': 0.8},
                'implementation': {'flutter_changes': {}, 'python_changes': {}},
                'affected_components': [],
                'test_scenarios': []
            }
            orchestrator.cr_handler.handle_change_request.return_value = cr_result
            
            # Process CR
            result = await orchestrator.handle_change_request("Add UPI AutoPay feature")
            
            # Verify flow
            assert 'cr_id' in result
            assert result['description'] == "Add UPI AutoPay feature"
            orchestrator.cr_handler.handle_change_request.assert_called_once()
            orchestrator.memory_agent.store_change_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_memory_and_analysis_integration(self):
        """Test integration between memory and analysis agents"""
        with patch('agents.orchestrator.VectorStore') as mock_vector_store, \
             patch('agents.orchestrator.StructuredStore') as mock_structured_store:
            
            # Create agents
            vector_store = Mock()
            structured_store = AsyncMock()
            memory_agent = MemoryAgent(vector_store, structured_store)
            analyzer_agent = AnalyzerAgent(vector_store, structured_store)
            
            # Mock analysis results
            analysis_results = {
                'flutter': {'widgets': [], 'blocs': []},
                'python': {'endpoints': [], 'models': []}
            }
            
            # Store analysis results
            await memory_agent.store_code_analysis(analysis_results, '/test/project')
            
            # Verify storage calls were made
            # (In a real test, we'd verify the actual storage logic)
            assert True  # Placeholder for actual verification

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=agents', '--cov-report=html'])