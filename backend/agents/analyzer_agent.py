import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from analyzers.flutter_analyzer import FlutterAnalyzer
from analyzers.python_analyzer import PythonAnalyzer
from memory.vector_store import VectorStore
from memory.structured_store import StructuredStore

class AnalyzerAgent:
    """Agent responsible for coordinating code analysis"""
    
    def __init__(self, vector_store: VectorStore, structured_store: StructuredStore):
        self.vector_store = vector_store
        self.structured_store = structured_store
        self.flutter_analyzer = FlutterAnalyzer()
        self.python_analyzer = PythonAnalyzer()
        
        self.analysis_cache = {}
        self.last_analysis_time = {}
    
    async def analyze_project_incremental(self, project_path: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Perform incremental analysis of the project"""
        
        cache_key = project_path
        
        # Check if we need to refresh
        if not force_refresh and cache_key in self.analysis_cache:
            last_analysis = self.last_analysis_time.get(cache_key)
            if last_analysis and (datetime.now() - last_analysis).seconds < 3600:  # 1 hour cache
                return self.analysis_cache[cache_key]
        
        # Perform full analysis
        results = await self.analyze_project_full(project_path)
        
        # Cache results
        self.analysis_cache[cache_key] = results
        self.last_analysis_time[cache_key] = datetime.now()
        
        return results
    
    async def analyze_project_full(self, project_path: str) -> Dict[str, Any]:
        """Perform full analysis of the project"""
        
        print(f"Starting full project analysis: {project_path}")
        
        # Analyze Flutter code
        flutter_results = await self._analyze_flutter_code(project_path)
        
        # Analyze Python code
        python_results = await self._analyze_python_code(project_path)
        
        # Perform cross-analysis
        cross_analysis = await self._perform_cross_analysis(flutter_results, python_results)
        
        # Generate insights
        insights = self._generate_insights(flutter_results, python_results, cross_analysis)
        
        results = {
            'flutter': flutter_results,
            'python': python_results,
            'cross_analysis': cross_analysis,
            'insights': insights,
            'analysis_timestamp': datetime.now().isoformat(),
            'project_path': project_path
        }
        
        print(f"Analysis complete. Found {len(flutter_results.get('widgets', []))} Flutter widgets, {len(python_results.get('endpoints', []))} Python endpoints")
        
        return results
    
    async def analyze_single_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file"""
        
        if file_path.endswith('.dart'):
            return self.flutter_analyzer.analyze_dart_file(file_path)
        elif file_path.endswith('.py'):
            return self.python_analyzer.analyze_python_file(file_path)
        else:
            return {'error': f'Unsupported file type: {file_path}'}
    
    async def get_code_metrics(self, project_path: str) -> Dict[str, Any]:
        """Get code quality metrics"""
        
        analysis = await self.analyze_project_incremental(project_path)
        
        flutter_metrics = self._calculate_flutter_metrics(analysis.get('flutter', {}))
        python_metrics = self._calculate_python_metrics(analysis.get('python', {}))
        
        return {
            'flutter_metrics': flutter_metrics,
            'python_metrics': python_metrics,
            'overall_metrics': self._calculate_overall_metrics(flutter_metrics, python_metrics),
            'recommendations': self._generate_recommendations(flutter_metrics, python_metrics)
        }
    
    async def find_code_patterns(self, project_path: str, pattern_type: str) -> List[Dict[str, Any]]:
        """Find specific code patterns in the project"""
        
        analysis = await self.analyze_project_incremental(project_path)
        
        if pattern_type == 'api_calls':
            return self._find_api_call_patterns(analysis)
        elif pattern_type == 'state_management':
            return self._find_state_management_patterns(analysis)
        elif pattern_type == 'navigation':
            return self._find_navigation_patterns(analysis)
        elif pattern_type == 'validation':
            return self._find_validation_patterns(analysis)
        else:
            return []
    
    async def get_dependency_graph(self, project_path: str) -> Dict[str, Any]:
        """Generate dependency graph for the project"""
        
        analysis = await self.analyze_project_incremental(project_path)
        
        flutter_deps = self._extract_flutter_dependencies(analysis.get('flutter', {}))
        python_deps = self._extract_python_dependencies(analysis.get('python', {}))
        
        return {
            'flutter_dependencies': flutter_deps,
            'python_dependencies': python_deps,
            'cross_dependencies': analysis.get('cross_analysis', {}).get('api_mappings', [])
        }
    
    async def _analyze_flutter_code(self, project_path: str) -> Dict[str, Any]:
        """Analyze Flutter code in the project"""
        
        flutter_path = f"{project_path}/mobile" if "/mobile" not in project_path else project_path
        
        try:
            return self.flutter_analyzer.analyze_project(flutter_path)
        except Exception as e:
            print(f"Error analyzing Flutter code: {e}")
            return {}
    
    async def _analyze_python_code(self, project_path: str) -> Dict[str, Any]:
        """Analyze Python code in the project"""
        
        python_path = f"{project_path}/backend" if "/backend" not in project_path else project_path
        
        try:
            return self.python_analyzer.analyze_project(python_path)
        except Exception as e:
            print(f"Error analyzing Python code: {e}")
            return {}
    
    async def _perform_cross_analysis(self, flutter_results: Dict[str, Any], python_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cross-analysis between Flutter and Python code"""
        
        # Find API call mappings
        api_mappings = self._map_api_calls(flutter_results, python_results)
        
        # Find data model mappings
        model_mappings = self._map_data_models(flutter_results, python_results)
        
        # Find validation mappings
        validation_mappings = self._map_validations(flutter_results, python_results)
        
        return {
            'api_mappings': api_mappings,
            'model_mappings': model_mappings,
            'validation_mappings': validation_mappings,
            'coverage_analysis': self._analyze_coverage(api_mappings, model_mappings)
        }
    
    def _generate_insights(self, flutter_results: Dict[str, Any], python_results: Dict[str, Any], cross_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from the analysis"""
        
        insights = {
            'architecture_patterns': [],
            'potential_issues': [],
            'optimization_opportunities': [],
            'best_practices': []
        }
        
        # Analyze architecture patterns
        if flutter_results.get('blocs'):
            insights['architecture_patterns'].append('BLoC pattern detected in Flutter')
        
        if any('Provider' in str(dep) for dep in flutter_results.get('dependencies', {}).get('dependencies', [])):
            insights['architecture_patterns'].append('Provider pattern detected in Flutter')
        
        # Identify potential issues
        api_mappings = cross_analysis.get('api_mappings', [])
        unmapped_apis = [api for api in flutter_results.get('api_calls', []) if not any(api['endpoint'] in mapping['flutter_endpoint'] for mapping in api_mappings)]
        
        if unmapped_apis:
            insights['potential_issues'].append(f'Found {len(unmapped_apis)} unmapped API calls')
        
        # Optimization opportunities
        if len(flutter_results.get('widgets', [])) > 50:
            insights['optimization_opportunities'].append('Consider widget optimization - large number of widgets detected')
        
        if len(python_results.get('endpoints', [])) > 30:
            insights['optimization_opportunities'].append('Consider API endpoint consolidation')
        
        # Best practices
        if flutter_results.get('form_validators'):
            insights['best_practices'].append('Good: Form validation implemented')
        
        if python_results.get('validators'):
            insights['best_practices'].append('Good: Backend validation implemented')
        
        return insights
    
    def _map_api_calls(self, flutter_results: Dict[str, Any], python_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map Flutter API calls to Python endpoints"""
        
        mappings = []
        flutter_api_calls = flutter_results.get('api_calls', [])
        python_endpoints = python_results.get('endpoints', [])
        
        for api_call in flutter_api_calls:
            flutter_endpoint = api_call.get('endpoint', '')
            flutter_method = api_call.get('method', '')
            
            for endpoint in python_endpoints:
                if self._endpoints_match(flutter_endpoint, endpoint.path) and flutter_method.upper() == endpoint.method:
                    mappings.append({
                        'flutter_endpoint': flutter_endpoint,
                        'flutter_method': flutter_method,
                        'flutter_file': api_call.get('file_path'),
                        'python_endpoint': endpoint.path,
                        'python_method': endpoint.method,
                        'python_file': endpoint.file_path,
                        'python_function': endpoint.name,
                        'confidence': 0.9
                    })
        
        return mappings
    
    def _map_data_models(self, flutter_results: Dict[str, Any], python_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map data models between Flutter and Python"""
        
        mappings = []
        # This would implement model mapping logic
        # For now, return empty list
        return mappings
    
    def _map_validations(self, flutter_results: Dict[str, Any], python_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map validation logic between Flutter and Python"""
        
        mappings = []
        flutter_validators = flutter_results.get('form_validators', [])
        python_validators = python_results.get('validators', [])
        
        # Simple mapping based on similar validation patterns
        for flutter_val in flutter_validators:
            for python_val in python_validators:
                if self._validators_similar(flutter_val, python_val):
                    mappings.append({
                        'flutter_validator': flutter_val,
                        'python_validator': python_val,
                        'similarity': 0.7
                    })
        
        return mappings
    
    def _analyze_coverage(self, api_mappings: List[Dict[str, Any]], model_mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze coverage of mappings"""
        
        return {
            'api_coverage': len(api_mappings),
            'model_coverage': len(model_mappings),
            'overall_coverage': 'good' if len(api_mappings) > 5 else 'needs_improvement'
        }
    
    def _calculate_flutter_metrics(self, flutter_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Flutter code metrics"""
        
        widgets = flutter_results.get('widgets', [])
        blocs = flutter_results.get('blocs', [])
        api_calls = flutter_results.get('api_calls', [])
        
        return {
            'total_widgets': len(widgets),
            'stateless_widgets': len([w for w in widgets if w.type == 'StatelessWidget']),
            'stateful_widgets': len([w for w in widgets if w.type == 'StatefulWidget']),
            'total_blocs': len(blocs),
            'total_api_calls': len(api_calls),
            'average_widget_complexity': self._calculate_widget_complexity(widgets),
            'code_reusability': self._calculate_reusability(widgets)
        }
    
    def _calculate_python_metrics(self, python_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Python code metrics"""
        
        endpoints = python_results.get('endpoints', [])
        models = python_results.get('models', [])
        services = python_results.get('services', [])
        
        return {
            'total_endpoints': len(endpoints),
            'total_models': len(models),
            'total_services': len(services),
            'api_coverage': len(endpoints),
            'model_complexity': self._calculate_model_complexity(models),
            'service_complexity': self._calculate_service_complexity(services)
        }
    
    def _calculate_overall_metrics(self, flutter_metrics: Dict[str, Any], python_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall project metrics"""
        
        return {
            'total_components': flutter_metrics['total_widgets'] + python_metrics['total_endpoints'],
            'architecture_score': self._calculate_architecture_score(flutter_metrics, python_metrics),
            'maintainability_score': self._calculate_maintainability_score(flutter_metrics, python_metrics),
            'test_coverage_estimate': 'medium'  # Would be calculated from actual test files
        }
    
    def _generate_recommendations(self, flutter_metrics: Dict[str, Any], python_metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on metrics"""
        
        recommendations = []
        
        if flutter_metrics['total_widgets'] > 50:
            recommendations.append('Consider breaking down large widgets into smaller, reusable components')
        
        if python_metrics['total_endpoints'] > 30:
            recommendations.append('Consider grouping related endpoints into separate routers')
        
        if flutter_metrics['average_widget_complexity'] > 0.7:
            recommendations.append('Some widgets have high complexity - consider refactoring')
        
        if python_metrics['model_complexity'] > 0.8:
            recommendations.append('Some models are complex - consider breaking them down')
        
        return recommendations
    
    def _find_api_call_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find API call patterns"""
        
        patterns = []
        flutter_api_calls = analysis.get('flutter', {}).get('api_calls', [])
        
        # Group by endpoint
        endpoint_groups = {}
        for api_call in flutter_api_calls:
            endpoint = api_call.get('endpoint', '')
            if endpoint not in endpoint_groups:
                endpoint_groups[endpoint] = []
            endpoint_groups[endpoint].append(api_call)
        
        for endpoint, calls in endpoint_groups.items():
            if len(calls) > 1:
                patterns.append({
                    'pattern_type': 'repeated_api_call',
                    'endpoint': endpoint,
                    'occurrences': len(calls),
                    'files': [call.get('file_path') for call in calls]
                })
        
        return patterns
    
    def _find_state_management_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find state management patterns"""
        
        patterns = []
        flutter_results = analysis.get('flutter', {})
        
        if flutter_results.get('blocs'):
            patterns.append({
                'pattern_type': 'bloc_pattern',
                'count': len(flutter_results['blocs']),
                'details': flutter_results['blocs']
            })
        
        return patterns
    
    def _find_navigation_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find navigation patterns"""
        
        patterns = []
        flutter_routes = analysis.get('flutter', {}).get('routes', [])
        
        # Group by navigation type
        nav_types = {}
        for route in flutter_routes:
            nav_type = route.get('type', 'unknown')
            if nav_type not in nav_types:
                nav_types[nav_type] = []
            nav_types[nav_type].append(route)
        
        for nav_type, routes in nav_types.items():
            patterns.append({
                'pattern_type': f'navigation_{nav_type}',
                'count': len(routes),
                'routes': [route.get('route') for route in routes]
            })
        
        return patterns
    
    def _find_validation_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find validation patterns"""
        
        patterns = []
        
        flutter_validators = analysis.get('flutter', {}).get('form_validators', [])
        python_validators = analysis.get('python', {}).get('validators', [])
        
        if flutter_validators:
            patterns.append({
                'pattern_type': 'flutter_validation',
                'count': len(flutter_validators),
                'validators': flutter_validators
            })
        
        if python_validators:
            patterns.append({
                'pattern_type': 'python_validation',
                'count': len(python_validators),
                'validators': python_validators
            })
        
        return patterns
    
    def _extract_flutter_dependencies(self, flutter_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Flutter dependencies"""
        
        return {
            'pubspec_dependencies': flutter_results.get('dependencies', {}),
            'widget_dependencies': [
                {
                    'widget': widget.name,
                    'dependencies': widget.dependencies
                }
                for widget in flutter_results.get('widgets', [])
            ]
        }
    
    def _extract_python_dependencies(self, python_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Python dependencies"""
        
        return {
            'package_dependencies': python_results.get('dependencies', {}),
            'module_dependencies': [
                {
                    'endpoint': endpoint.name,
                    'dependencies': endpoint.dependencies
                }
                for endpoint in python_results.get('endpoints', [])
            ]
        }
    
    def _endpoints_match(self, flutter_endpoint: str, python_endpoint: str) -> bool:
        """Check if Flutter and Python endpoints match"""
        
        # Simple matching logic
        flutter_clean = flutter_endpoint.strip('/').lower()
        python_clean = python_endpoint.strip('/').lower()
        
        return flutter_clean in python_clean or python_clean in flutter_clean
    
    def _validators_similar(self, flutter_validator: Dict[str, Any], python_validator: Dict[str, Any]) -> bool:
        """Check if validators are similar"""
        
        # Simple similarity check
        flutter_code = str(flutter_validator.get('code', '')).lower()
        python_name = str(python_validator.get('name', '')).lower()
        
        return any(keyword in flutter_code and keyword in python_name 
                  for keyword in ['email', 'phone', 'required', 'length', 'pattern'])
    
    def _calculate_widget_complexity(self, widgets: List[Any]) -> float:
        """Calculate average widget complexity"""
        
        if not widgets:
            return 0.0
        
        total_complexity = 0
        for widget in widgets:
            complexity = (
                len(widget.dependencies) * 0.1 +
                len(widget.api_calls) * 0.2 +
                len(widget.form_fields) * 0.1 +
                len(widget.validators) * 0.1
            )
            total_complexity += min(complexity, 1.0)  # Cap at 1.0
        
        return total_complexity / len(widgets)
    
    def _calculate_reusability(self, widgets: List[Any]) -> float:
        """Calculate code reusability score"""
        
        if not widgets:
            return 0.0
        
        # Simple heuristic: widgets with fewer dependencies are more reusable
        reusable_widgets = [w for w in widgets if len(w.dependencies) <= 3]
        return len(reusable_widgets) / len(widgets)
    
    def _calculate_model_complexity(self, models: List[Any]) -> float:
        """Calculate average model complexity"""
        
        if not models:
            return 0.0
        
        total_complexity = 0
        for model in models:
            complexity = (
                len(model.fields) * 0.1 +
                len(model.validators) * 0.2
            )
            total_complexity += min(complexity, 1.0)
        
        return total_complexity / len(models)
    
    def _calculate_service_complexity(self, services: List[Any]) -> float:
        """Calculate average service complexity"""
        
        if not services:
            return 0.0
        
        total_complexity = 0
        for service in services:
            complexity = (
                len(service.parameters) * 0.1 +
                len(service.database_operations) * 0.2 +
                len(service.external_calls) * 0.3
            )
            total_complexity += min(complexity, 1.0)
        
        return total_complexity / len(services)
    
    def _calculate_architecture_score(self, flutter_metrics: Dict[str, Any], python_metrics: Dict[str, Any]) -> float:
        """Calculate architecture quality score"""
        
        score = 0.5  # Base score
        
        # Bonus for good patterns
        if flutter_metrics['total_blocs'] > 0:
            score += 0.1
        
        if python_metrics['total_services'] > 0:
            score += 0.1
        
        # Penalty for complexity
        if flutter_metrics['average_widget_complexity'] > 0.8:
            score -= 0.1
        
        if python_metrics['model_complexity'] > 0.8:
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _calculate_maintainability_score(self, flutter_metrics: Dict[str, Any], python_metrics: Dict[str, Any]) -> float:
        """Calculate maintainability score"""
        
        score = 0.5  # Base score
        
        # Bonus for reusability
        score += flutter_metrics['code_reusability'] * 0.2
        
        # Bonus for good structure
        if flutter_metrics['stateless_widgets'] > flutter_metrics['stateful_widgets']:
            score += 0.1
        
        # Penalty for too many components
        total_components = flutter_metrics['total_widgets'] + python_metrics['total_endpoints']
        if total_components > 100:
            score -= 0.2
        
        return max(0.0, min(1.0, score))