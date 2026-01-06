import asyncio
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime

from analyzers.flutter_analyzer import FlutterAnalyzer
from analyzers.python_analyzer import PythonAnalyzer
from memory.vector_store import VectorStore
from memory.structured_store import StructuredStore, CodeEntity, Relationship
from agents.memory_agent import MemoryAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.cr_handler_agent import CRHandlerAgent
from ingestion import parser as ingestion_parser

class AgentOrchestrator:
    """Main orchestrator that coordinates all agents"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.structured_store = StructuredStore()
        self.memory_agent = MemoryAgent(self.vector_store, self.structured_store)
        self.analyzer_agent = AnalyzerAgent(self.vector_store, self.structured_store)
        self.cr_handler = CRHandlerAgent(self.vector_store, self.structured_store)
        
        self.flutter_analyzer = FlutterAnalyzer()
        self.python_analyzer = PythonAnalyzer()
        
        self.analysis_cache = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize the orchestrator and all components"""
        if not self.initialized:
            await self.structured_store.init_db()
            self.initialized = True
    
    async def analyze_codebase(self, project_path: str) -> Dict[str, Any]:
        """Analyze entire codebase and store in memory"""
        await self.initialize()
        
        print(f"Starting codebase analysis for: {project_path}")
        
        # Analyze Flutter code
        flutter_results = await self._analyze_flutter_project(project_path)
        
        # Analyze Python code
        python_results = await self._analyze_python_project(project_path)
        
        # Store analysis results
        await self._store_analysis_results(flutter_results, python_results)
        
        # Create cross-language mappings
        await self._create_api_mappings(flutter_results, python_results)
        
        analysis_summary = {
            'flutter': {
                'widgets': len(flutter_results.get('widgets', [])),
                'blocs': len(flutter_results.get('blocs', [])),
                'api_calls': len(flutter_results.get('api_calls', [])),
                'routes': len(flutter_results.get('routes', []))
            },
            'python': {
                'endpoints': len(python_results.get('endpoints', [])),
                'models': len(python_results.get('models', [])),
                'services': len(python_results.get('services', [])),
                'validators': len(python_results.get('validators', []))
            },
            'memory_stats': await self._get_memory_stats()
        }
        
        print(f"Analysis complete: {analysis_summary}")
        return analysis_summary

    async def ingest_brd_documents(self, paths: List[str], feature_area: str = "unspecified") -> Dict[str, Any]:
        """Ingest BRD/CR documents (DOCX/PDF/TXT) into memory."""
        await self.initialize()

        all_requirements: List[Dict[str, Any]] = []
        for path in paths:
            try:
                reqs = ingestion_parser.parse_brd_document(path, feature_area=feature_area)
                all_requirements.extend(reqs)
            except Exception as exc:
                print(f"Error ingesting BRD {path}: {exc}")

        if all_requirements:
            await self.memory_agent.store_requirements(all_requirements)

        return {"ingested": len(all_requirements), "paths": paths}

    async def ingest_api_contracts(self, excel_path: str, sheet: str | int | None = None, column_map: Dict[str, str] | None = None) -> Dict[str, Any]:
        """Ingest API contracts from Excel into memory."""
        await self.initialize()

        try:
            contracts = ingestion_parser.parse_api_excel(excel_path, sheet=sheet, column_map=column_map)
        except Exception as exc:
            print(f"Error ingesting API Excel {excel_path}: {exc}")
            contracts = []

        if contracts:
            await self.memory_agent.store_api_contracts(contracts)

        return {"ingested": len(contracts), "path": excel_path, "sheet": sheet}
    
    async def handle_change_request(self, cr_description: str, cr_id: Optional[str] = None) -> Dict[str, Any]:
        """Handle a change request"""
        await self.initialize()
        
        if not cr_id:
            cr_id = str(uuid.uuid4())
        
        print(f"Processing CR {cr_id}: {cr_description}")
        
        # Use CR handler to process the request
        cr_result = await self.cr_handler.handle_change_request(cr_id, cr_description)
        
        # Store the CR and its implementation in memory
        await self.memory_agent.store_change_request(cr_id, cr_description, cr_result)
        
        return {
            'cr_id': cr_id,
            'description': cr_description,
            'result': cr_result,
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_context_for_query(self, query: str, context_type: str = 'all') -> Dict[str, Any]:
        """Get relevant context for a query"""
        await self.initialize()
        
        if context_type == 'flutter':
            return self.vector_store.search_flutter_code(query)
        elif context_type == 'python':
            return self.vector_store.search_python_code(query)
        elif context_type == 'brd':
            return self.vector_store.search_brd_content(query)
        elif context_type == 'cr':
            return self.vector_store.search_similar_crs(query)
        else:
            return self.vector_store.search_all(query)
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        await self.initialize()
        
        return {
            'vector_store': self.vector_store.get_collection_stats(),
            'structured_store': await self.structured_store.get_stats(),
            'cache_size': len(self.analysis_cache)
        }
    
    async def _analyze_flutter_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze Flutter project"""
        flutter_path = f"{project_path}/mobile" if "/mobile" not in project_path else project_path
        
        try:
            results = self.flutter_analyzer.analyze_project(flutter_path)
            self.analysis_cache['flutter'] = results
            return results
        except Exception as e:
            print(f"Error analyzing Flutter project: {e}")
            return {}
    
    async def _analyze_python_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze Python project"""
        python_path = f"{project_path}/backend" if "/backend" not in project_path else project_path
        
        try:
            results = self.python_analyzer.analyze_project(python_path)
            self.analysis_cache['python'] = results
            return results
        except Exception as e:
            print(f"Error analyzing Python project: {e}")
            return {}
    
    async def _store_analysis_results(self, flutter_results: Dict[str, Any], python_results: Dict[str, Any]):
        """Store analysis results in memory stores"""
        
        # Store Flutter widgets
        for widget in flutter_results.get('widgets', []):
            entity_id = f"flutter_widget_{widget.name}_{hash(widget.file_path)}"
            entity = CodeEntity(
                id=entity_id,
                type='widget',
                name=widget.name,
                file_path=widget.file_path,
                language='dart',
                metadata={
                    'widget_type': widget.type,
                    'dependencies': widget.dependencies,
                    'api_calls': widget.api_calls,
                    'navigation_routes': widget.navigation_routes,
                    'form_fields': widget.form_fields,
                    'validators': widget.validators
                },
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            await self.structured_store.add_entity(entity)
            
            # Add to vector store
            widget_content = f"Widget: {widget.name}\nType: {widget.type}\nFile: {widget.file_path}\nDependencies: {', '.join(widget.dependencies)}\nAPI Calls: {', '.join(widget.api_calls)}"
            self.vector_store.add_flutter_code(widget.file_path, widget_content, entity.metadata)
        
        # Store Python endpoints
        for endpoint in python_results.get('endpoints', []):
            entity_id = f"python_endpoint_{endpoint.name}_{hash(endpoint.file_path)}"
            entity = CodeEntity(
                id=entity_id,
                type='api_endpoint',
                name=endpoint.name,
                file_path=endpoint.file_path,
                language='python',
                metadata={
                    'method': endpoint.method,
                    'path': endpoint.path,
                    'parameters': endpoint.parameters,
                    'return_type': endpoint.return_type,
                    'dependencies': endpoint.dependencies
                },
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            await self.structured_store.add_entity(entity)
            
            # Add to vector store
            endpoint_content = f"Endpoint: {endpoint.method} {endpoint.path}\nFunction: {endpoint.name}\nFile: {endpoint.file_path}\nParameters: {endpoint.parameters}"
            self.vector_store.add_python_code(endpoint.file_path, endpoint_content, entity.metadata)
        
        # Store Python models
        for model in python_results.get('models', []):
            entity_id = f"python_model_{model.name}_{hash(model.file_path)}"
            entity = CodeEntity(
                id=entity_id,
                type='model',
                name=model.name,
                file_path=model.file_path,
                language='python',
                metadata={
                    'fields': model.fields,
                    'base_classes': model.base_classes,
                    'validators': model.validators
                },
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            await self.structured_store.add_entity(entity)
            
            # Add to vector store
            model_content = f"Model: {model.name}\nFile: {model.file_path}\nFields: {[f['name'] for f in model.fields]}\nValidators: {model.validators}"
            self.vector_store.add_python_code(model.file_path, model_content, entity.metadata)
    
    async def _create_api_mappings(self, flutter_results: Dict[str, Any], python_results: Dict[str, Any]):
        """Create mappings between Flutter widgets and Python endpoints"""
        
        flutter_api_calls = flutter_results.get('api_calls', [])
        python_endpoints = python_results.get('endpoints', [])
        
        for api_call in flutter_api_calls:
            endpoint_path = api_call.get('endpoint', '')
            
            # Find matching Python endpoint
            for endpoint in python_endpoints:
                if endpoint.path in endpoint_path or endpoint_path in endpoint.path:
                    flutter_widget_id = f"flutter_api_call_{hash(api_call['file_path'])}_{api_call['line']}"
                    python_endpoint_id = f"python_endpoint_{endpoint.name}_{hash(endpoint.file_path)}"
                    
                    await self.structured_store.add_api_mapping(
                        flutter_widget_id,
                        python_endpoint_id,
                        'api_call',
                        {
                            'flutter_method': api_call.get('method'),
                            'python_method': endpoint.method,
                            'endpoint': endpoint_path,
                            'confidence': 0.8
                        }
                    )
    
    async def _get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            'vector_store': self.vector_store.get_collection_stats(),
            'structured_store': await self.structured_store.get_stats()
        }
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get cached analysis summary"""
        return {
            'flutter': self.analysis_cache.get('flutter', {}),
            'python': self.analysis_cache.get('python', {}),
            'last_updated': datetime.now().isoformat()
        }
    
    async def search_code(self, query: str, language: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search code across the codebase"""
        await self.initialize()
        
        if language == 'dart':
            return self.vector_store.search_flutter_code(query, limit)
        elif language == 'python':
            return self.vector_store.search_python_code(query, limit)
        else:
            results = self.vector_store.search_all(query, limit)
            # Flatten results
            all_results = []
            for category, items in results.items():
                all_results.extend(items)
            return sorted(all_results, key=lambda x: x.get('distance', 1.0))[:limit]
    
    async def get_related_code(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get code related to a specific entity"""
        await self.initialize()
        
        related_entities = await self.structured_store.get_related_entities(entity_id)
        return [
            {
                'id': entity.id,
                'name': entity.name,
                'type': entity.type,
                'file_path': entity.file_path,
                'language': entity.language,
                'metadata': entity.metadata
            }
            for entity in related_entities
        ]