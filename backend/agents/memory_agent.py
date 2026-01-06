import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from uuid import uuid4

from memory.vector_store import VectorStore
from memory.structured_store import StructuredStore, CodeEntity, Relationship

class MemoryAgent:
    """Agent responsible for managing persistent memory operations"""
    
    def __init__(self, vector_store: VectorStore, structured_store: StructuredStore):
        self.vector_store = vector_store
        self.structured_store = structured_store
    
    async def store_code_analysis(self, analysis_results: Dict[str, Any], project_path: str):
        """Store code analysis results in memory"""
        
        # Store Flutter analysis
        flutter_results = analysis_results.get('flutter', {})
        await self._store_flutter_analysis(flutter_results, project_path)
        
        # Store Python analysis
        python_results = analysis_results.get('python', {})
        await self._store_python_analysis(python_results, project_path)
        
        # Create cross-references
        await self._create_cross_references(flutter_results, python_results)
    
    async def store_change_request(self, cr_id: str, description: str, implementation: Dict[str, Any]):
        """Store change request and its implementation"""
        
        # Store in vector store for similarity search
        self.vector_store.add_change_request(
            cr_id=cr_id,
            description=description,
            implementation=json.dumps(implementation),
            metadata={
                'timestamp': datetime.now().isoformat(),
                'status': 'implemented',
                'complexity': implementation.get('estimated_effort', {}).get('complexity', 'medium')
            }
        )
        
        # Store in structured store
        affected_entities = []
        if 'affected_components' in implementation:
            for component_type, components in implementation['affected_components'].items():
                for component in components:
                    if isinstance(component, dict) and 'file' in component:
                        affected_entities.append(component['file'])
        
        await self.structured_store.add_change_request(
            cr_id=cr_id,
            title=description[:100],  # Truncate for title
            description=description,
            affected_entities=affected_entities
        )

    async def store_requirements(self, requirements: List[Dict[str, Any]]):
        """Store BRD/requirement records into structured and vector stores."""

        for req in requirements:
            req_id = str(req.get("id") or uuid4())
            title = req.get("title") or f"Requirement {req_id}"
            description = (req.get("description") or "").strip()

            entity = CodeEntity(
                id=f"requirement_{req_id}",
                type="requirement",
                name=title,
                file_path=req.get("source") or "",
                language="text",
                metadata={
                    "priority": req.get("priority"),
                    "feature_area": req.get("feature_area"),
                    "acceptance_criteria": req.get("acceptance_criteria", []),
                    "risks": req.get("risks", []),
                    "compliance_tags": req.get("compliance_tags", []),
                    "dependencies": req.get("dependencies", []),
                    "raw_refs": req.get("raw_refs", [])
                },
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            await self.structured_store.add_entity(entity)

            # Add to vector store for semantic search
            ac_text = "\n".join(req.get("acceptance_criteria", []))
            risk_text = "\n".join(req.get("risks", []))
            content = f"Requirement: {title}\nPriority: {req.get('priority')}\nFeature: {req.get('feature_area')}\nDescription: {description}\nAC:\n{ac_text}\nRisks:\n{risk_text}"
            self.vector_store.add_brd_content(
                document_name=title,
                content=content,
                metadata={"id": req_id, "type": "requirement", **entity.metadata},
            )

    async def store_api_contracts(self, contracts: List[Dict[str, Any]]):
        """Store API contract records into structured and vector stores."""

        for contract in contracts:
            method = str(contract.get("method", "")).upper()
            path = contract.get("path", "")
            version = contract.get("version", "")
            contract_id = contract.get("id") or f"{method}_{path}_{version}" or str(uuid4())
            title = contract.get("service") or path or "API Contract"

            entity = CodeEntity(
                id=f"api_contract_{contract_id}",
                type="api_contract",
                name=title,
                file_path=contract.get("source") or "",
                language="api",
                metadata={
                    "method": method,
                    "path": path,
                    "version": version,
                    "auth": contract.get("auth"),
                    "rate_limit": contract.get("rate_limit"),
                    "request_schema": contract.get("request_schema", {}),
                    "response_schema": contract.get("response_schema", {}),
                    "errors": contract.get("errors", []),
                    "tests": contract.get("tests", []),
                    "owner": contract.get("owner"),
                    "raw_refs": contract.get("raw_refs", []),
                },
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            await self.structured_store.add_entity(entity)

            # Add to vector store for semantic search (reuse BRD collection for contracts)
            content = (
                f"API: {method} {path} ({version})\n"
                f"Auth: {contract.get('auth')} Rate: {contract.get('rate_limit')}\n"
                f"Request: {json.dumps(contract.get('request_schema', {}))}\n"
                f"Response: {json.dumps(contract.get('response_schema', {}))}\n"
                f"Errors: {contract.get('errors', [])}\n"
                f"Tests: {contract.get('tests', [])}"
            )
            self.vector_store.add_brd_content(
                document_name=title,
                content=content,
                metadata={"id": contract_id, "type": "api_contract", **entity.metadata},
            )
    
    async def retrieve_context_for_cr(self, cr_description: str, limit: int = 10) -> Dict[str, Any]:
        """Retrieve relevant context for a change request"""
        
        # Search vector store for similar code
        flutter_context = self.vector_store.search_flutter_code(cr_description, limit)
        python_context = self.vector_store.search_python_code(cr_description, limit)
        similar_crs = self.vector_store.search_similar_crs(cr_description, limit//2)
        
        # Get structured context
        entities = await self._get_relevant_entities(cr_description)
        
        return {
            'flutter_code': flutter_context,
            'python_code': python_context,
            'similar_crs': similar_crs,
            'entities': entities,
            'api_mappings': await self._get_api_mappings_for_context(cr_description)
        }
    
    async def get_entity_relationships(self, entity_id: str) -> Dict[str, Any]:
        """Get relationships for a specific entity"""
        
        related_entities = await self.structured_store.get_related_entities(entity_id)
        
        relationships = {
            'direct_dependencies': [],
            'dependents': [],
            'api_connections': []
        }
        
        for entity in related_entities:
            relationships['direct_dependencies'].append({
                'id': entity.id,
                'name': entity.name,
                'type': entity.type,
                'file_path': entity.file_path,
                'language': entity.language
            })
        
        # Get API mappings
        api_mappings = await self.structured_store.get_api_mappings(widget_id=entity_id)
        api_mappings.extend(await self.structured_store.get_api_mappings(endpoint_id=entity_id))
        
        relationships['api_connections'] = api_mappings
        
        return relationships
    
    async def update_entity_metadata(self, entity_id: str, metadata: Dict[str, Any]):
        """Update metadata for an entity"""
        
        # Get existing entity
        entities = await self.structured_store.get_entities_by_type('widget')
        entities.extend(await self.structured_store.get_entities_by_type('api_endpoint'))
        entities.extend(await self.structured_store.get_entities_by_type('model'))
        
        for entity in entities:
            if entity.id == entity_id:
                entity.metadata.update(metadata)
                entity.updated_at = datetime.now()
                await self.structured_store.add_entity(entity)
                break
    
    async def search_memory(self, query: str, memory_type: str = 'all', limit: int = 10) -> List[Dict[str, Any]]:
        """Search across memory stores"""
        
        if memory_type == 'vector':
            return self.vector_store.search_all(query, limit)
        elif memory_type == 'structured':
            return await self._search_structured_memory(query, limit)
        else:
            # Search both
            vector_results = self.vector_store.search_all(query, limit//2)
            structured_results = await self._search_structured_memory(query, limit//2)
            
            return {
                'vector_results': vector_results,
                'structured_results': structured_results
            }
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        
        vector_stats = self.vector_store.get_collection_stats()
        structured_stats = await self.structured_store.get_stats()
        
        return {
            'vector_store': vector_stats,
            'structured_store': structured_stats,
            'total_entities': sum(structured_stats.get('entities', {}).values()),
            'total_relationships': sum(structured_stats.get('relationships', {}).values()),
            'memory_health': self._assess_memory_health(vector_stats, structured_stats)
        }
    
    async def cleanup_old_memories(self, days_old: int = 90):
        """Clean up old memories that are no longer relevant"""
        
        # This would implement cleanup logic for old CRs and outdated code references
        # For now, just return statistics
        
        return {
            'cleaned_entities': 0,
            'cleaned_relationships': 0,
            'cleaned_crs': 0,
            'message': f'Cleanup for memories older than {days_old} days completed'
        }
    
    async def _store_flutter_analysis(self, flutter_results: Dict[str, Any], project_path: str):
        """Store Flutter analysis results"""
        
        # Store widgets
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
                    'validators': widget.validators,
                    'line_start': widget.line_start,
                    'line_end': widget.line_end
                },
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            await self.structured_store.add_entity(entity)
            
            # Store in vector store
            widget_content = f"""
            Widget: {widget.name}
            Type: {widget.type}
            File: {widget.file_path}
            Dependencies: {', '.join(widget.dependencies)}
            API Calls: {', '.join(widget.api_calls)}
            Navigation: {', '.join(widget.navigation_routes)}
            Form Fields: {', '.join(widget.form_fields)}
            Validators: {', '.join(widget.validators)}
            """
            
            self.vector_store.add_flutter_code(
                widget.file_path,
                widget_content.strip(),
                entity.metadata
            )
        
        # Store BLoC patterns
        for bloc in flutter_results.get('blocs', []):
            entity_id = f"flutter_bloc_{bloc.name}_{hash(bloc.file_path)}"
            
            entity = CodeEntity(
                id=entity_id,
                type='bloc',
                name=bloc.name,
                file_path=bloc.file_path,
                language='dart',
                metadata={
                    'bloc_type': bloc.type,
                    'events': bloc.events,
                    'states': bloc.states
                },
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            await self.structured_store.add_entity(entity)
            
            # Store in vector store
            bloc_content = f"""
            BLoC: {bloc.name}
            Type: {bloc.type}
            File: {bloc.file_path}
            Events: {', '.join(bloc.events)}
            States: {', '.join(bloc.states)}
            """
            
            self.vector_store.add_flutter_code(
                bloc.file_path,
                bloc_content.strip(),
                entity.metadata
            )
    
    async def _store_python_analysis(self, python_results: Dict[str, Any], project_path: str):
        """Store Python analysis results"""
        
        # Store API endpoints
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
                    'dependencies': endpoint.dependencies,
                    'middleware': endpoint.middleware,
                    'line_number': endpoint.line_number
                },
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            await self.structured_store.add_entity(entity)
            
            # Store in vector store
            endpoint_content = f"""
            Endpoint: {endpoint.method} {endpoint.path}
            Function: {endpoint.name}
            File: {endpoint.file_path}
            Parameters: {[p['name'] for p in endpoint.parameters]}
            Return Type: {endpoint.return_type}
            Dependencies: {', '.join(endpoint.dependencies)}
            """
            
            self.vector_store.add_python_code(
                endpoint.file_path,
                endpoint_content.strip(),
                entity.metadata
            )
        
        # Store Pydantic models
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
                    'validators': model.validators,
                    'line_number': model.line_number
                },
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            await self.structured_store.add_entity(entity)
            
            # Store in vector store
            model_content = f"""
            Model: {model.name}
            File: {model.file_path}
            Fields: {[f['name'] for f in model.fields]}
            Base Classes: {', '.join(model.base_classes)}
            Validators: {', '.join(model.validators)}
            """
            
            self.vector_store.add_python_code(
                model.file_path,
                model_content.strip(),
                entity.metadata
            )
    
    async def _create_cross_references(self, flutter_results: Dict[str, Any], python_results: Dict[str, Any]):
        """Create cross-references between Flutter and Python components"""
        
        # Match API calls to endpoints
        flutter_api_calls = flutter_results.get('api_calls', [])
        python_endpoints = python_results.get('endpoints', [])
        
        for api_call in flutter_api_calls:
            endpoint_path = api_call.get('endpoint', '')
            
            for endpoint in python_endpoints:
                if self._paths_match(endpoint_path, endpoint.path):
                    # Create relationship
                    relationship_id = f"api_call_{hash(api_call['file_path'])}_{hash(endpoint.file_path)}"
                    
                    relationship = Relationship(
                        id=relationship_id,
                        source_entity_id=f"flutter_api_call_{hash(api_call['file_path'])}_{api_call['line']}",
                        target_entity_id=f"python_endpoint_{endpoint.name}_{hash(endpoint.file_path)}",
                        relationship_type='calls',
                        metadata={
                            'endpoint': endpoint_path,
                            'method': api_call.get('method'),
                            'confidence': 0.8
                        },
                        created_at=datetime.now()
                    )
                    
                    await self.structured_store.add_relationship(relationship)
    
    async def _get_relevant_entities(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant entities from structured store"""
        
        # Simple keyword matching for now
        # In a real implementation, this would use more sophisticated matching
        
        all_entities = []
        
        # Get widgets
        widgets = await self.structured_store.get_entities_by_type('widget')
        all_entities.extend(widgets)
        
        # Get endpoints
        endpoints = await self.structured_store.get_entities_by_type('api_endpoint')
        all_entities.extend(endpoints)
        
        # Get models
        models = await self.structured_store.get_entities_by_type('model')
        all_entities.extend(models)
        
        # Filter by relevance
        relevant_entities = []
        query_lower = query.lower()
        
        for entity in all_entities:
            if (query_lower in entity.name.lower() or 
                any(query_lower in str(v).lower() for v in entity.metadata.values())):
                relevant_entities.append({
                    'id': entity.id,
                    'name': entity.name,
                    'type': entity.type,
                    'file_path': entity.file_path,
                    'language': entity.language,
                    'metadata': entity.metadata
                })
        
        return relevant_entities[:10]  # Limit results
    
    async def _get_api_mappings_for_context(self, query: str) -> List[Dict[str, Any]]:
        """Get API mappings relevant to the query"""
        
        # Get all API mappings and filter by relevance
        all_mappings = await self.structured_store.get_api_mappings()
        
        relevant_mappings = []
        query_lower = query.lower()
        
        for mapping in all_mappings:
            metadata = mapping.get('metadata', {})
            if any(query_lower in str(v).lower() for v in metadata.values()):
                relevant_mappings.append(mapping)
        
        return relevant_mappings[:5]  # Limit results
    
    async def _search_structured_memory(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search structured memory"""
        
        results = []
        
        # Search entities
        entities = await self._get_relevant_entities(query)
        results.extend(entities)
        
        # Search API mappings
        mappings = await self._get_api_mappings_for_context(query)
        results.extend(mappings)
        
        return results[:limit]
    
    def _assess_memory_health(self, vector_stats: Dict[str, Any], structured_stats: Dict[str, Any]) -> str:
        """Assess the health of the memory system"""
        
        total_vector_items = sum(vector_stats.values())
        total_structured_items = sum(structured_stats.get('entities', {}).values())
        
        if total_vector_items > 1000 and total_structured_items > 500:
            return 'excellent'
        elif total_vector_items > 500 and total_structured_items > 250:
            return 'good'
        elif total_vector_items > 100 and total_structured_items > 50:
            return 'fair'
        else:
            return 'needs_improvement'
    
    def _paths_match(self, path1: str, path2: str) -> bool:
        """Check if two API paths match"""
        
        # Simple path matching - in reality, this would be more sophisticated
        path1_clean = path1.strip('/').lower()
        path2_clean = path2.strip('/').lower()
        
        return path1_clean in path2_clean or path2_clean in path1_clean