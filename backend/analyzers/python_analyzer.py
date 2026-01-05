import ast
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import inspect

@dataclass
class APIEndpoint:
    name: str
    method: str  # GET, POST, PUT, DELETE
    path: str
    function_name: str
    file_path: str
    line_number: int
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    dependencies: List[str]
    middleware: List[str]

@dataclass
class PydanticModel:
    name: str
    file_path: str
    line_number: int
    fields: List[Dict[str, Any]]
    base_classes: List[str]
    validators: List[str]

@dataclass
class ServiceFunction:
    name: str
    file_path: str
    line_number: int
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    database_operations: List[str]
    external_calls: List[str]

class PythonAnalyzer:
    """Analyzes Python code to extract FastAPI routes, models, and services"""
    
    def __init__(self):
        self.endpoints = []
        self.models = []
        self.services = []
        self.dependencies = {}
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze entire Python project"""
        results = {
            'endpoints': [],
            'models': [],
            'services': [],
            'middleware': [],
            'database_models': [],
            'validators': [],
            'dependencies': {}
        }
        
        # Analyze requirements.txt
        requirements_path = os.path.join(project_path, 'requirements.txt')
        if os.path.exists(requirements_path):
            results['dependencies'] = self._analyze_requirements(requirements_path)
        
        # Analyze Python files
        for root, dirs, files in os.walk(project_path):
            # Skip virtual environments and cache directories
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_results = self.analyze_python_file(file_path)
                    
                    results['endpoints'].extend(file_results.get('endpoints', []))
                    results['models'].extend(file_results.get('models', []))
                    results['services'].extend(file_results.get('services', []))
                    results['middleware'].extend(file_results.get('middleware', []))
                    results['database_models'].extend(file_results.get('database_models', []))
                    results['validators'].extend(file_results.get('validators', []))
        
        return results
    
    def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            return {
                'endpoints': self._extract_fastapi_endpoints(tree, content, file_path),
                'models': self._extract_pydantic_models(tree, content, file_path),
                'services': self._extract_service_functions(tree, content, file_path),
                'middleware': self._extract_middleware(tree, content, file_path),
                'database_models': self._extract_sqlalchemy_models(tree, content, file_path),
                'validators': self._extract_validators(tree, content, file_path),
                'imports': self._extract_imports(tree),
                'classes': self._extract_classes(tree, file_path),
                'functions': self._extract_functions(tree, file_path)
            }
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return {}
    
    def _extract_fastapi_endpoints(self, tree: ast.AST, content: str, file_path: str) -> List[APIEndpoint]:
        """Extract FastAPI route endpoints"""
        endpoints = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for FastAPI decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            # router.get, router.post, etc.
                            if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                method = decorator.func.attr.upper()
                                path = self._extract_path_from_decorator(decorator)
                                
                                endpoint = APIEndpoint(
                                    name=node.name,
                                    method=method,
                                    path=path,
                                    function_name=node.name,
                                    file_path=file_path,
                                    line_number=node.lineno,
                                    parameters=self._extract_function_parameters(node),
                                    return_type=self._extract_return_type(node),
                                    dependencies=self._extract_endpoint_dependencies(node),
                                    middleware=self._extract_endpoint_middleware(node)
                                )
                                endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_pydantic_models(self, tree: ast.AST, content: str, file_path: str) -> List[PydanticModel]:
        """Extract Pydantic models"""
        models = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from BaseModel
                base_classes = [self._get_name(base) for base in node.bases]
                if any('BaseModel' in base for base in base_classes):
                    model = PydanticModel(
                        name=node.name,
                        file_path=file_path,
                        line_number=node.lineno,
                        fields=self._extract_model_fields(node),
                        base_classes=base_classes,
                        validators=self._extract_model_validators(node)
                    )
                    models.append(model)
        
        return models
    
    def _extract_service_functions(self, tree: ast.AST, content: str, file_path: str) -> List[ServiceFunction]:
        """Extract service layer functions"""
        services = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions and class methods for now
                if not node.name.startswith('_') and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in getattr(parent, 'body', [])):
                    service = ServiceFunction(
                        name=node.name,
                        file_path=file_path,
                        line_number=node.lineno,
                        parameters=self._extract_function_parameters(node),
                        return_type=self._extract_return_type(node),
                        database_operations=self._extract_db_operations(node),
                        external_calls=self._extract_external_calls(node)
                    )
                    services.append(service)
        
        return services
    
    def _extract_sqlalchemy_models(self, tree: ast.AST, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract SQLAlchemy database models"""
        db_models = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                base_classes = [self._get_name(base) for base in node.bases]
                if any('Base' in base or 'Model' in base for base in base_classes):
                    db_model = {
                        'name': node.name,
                        'file_path': file_path,
                        'line_number': node.lineno,
                        'base_classes': base_classes,
                        'columns': self._extract_sqlalchemy_columns(node),
                        'relationships': self._extract_sqlalchemy_relationships(node),
                        'table_name': self._extract_table_name(node)
                    }
                    db_models.append(db_model)
        
        return db_models
    
    def _extract_validators(self, tree: ast.AST, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract validator functions"""
        validators = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if 'validate' in node.name.lower() or any(
                    isinstance(decorator, ast.Name) and 'validator' in decorator.id.lower()
                    for decorator in node.decorator_list
                    if isinstance(decorator, ast.Name)
                ):
                    validator = {
                        'name': node.name,
                        'file_path': file_path,
                        'line_number': node.lineno,
                        'parameters': self._extract_function_parameters(node),
                        'validation_logic': self._extract_validation_logic(node)
                    }
                    validators.append(validator)
        
        return validators
    
    def _extract_middleware(self, tree: ast.AST, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract middleware components"""
        middleware = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if 'middleware' in node.name.lower():
                    middleware_info = {
                        'name': node.name,
                        'file_path': file_path,
                        'line_number': node.lineno,
                        'methods': [method.name for method in node.body if isinstance(method, ast.FunctionDef)]
                    }
                    middleware.append(middleware_info)
        
        return middleware
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        return imports
    
    def _extract_classes(self, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """Extract all classes"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'file_path': file_path,
                    'line_number': node.lineno,
                    'base_classes': [self._get_name(base) for base in node.bases],
                    'methods': [method.name for method in node.body if isinstance(method, ast.FunctionDef)],
                    'decorators': [self._get_name(decorator) for decorator in node.decorator_list]
                }
                classes.append(class_info)
        
        return classes
    
    def _extract_functions(self, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """Extract all functions"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_info = {
                    'name': node.name,
                    'file_path': file_path,
                    'line_number': node.lineno,
                    'parameters': self._extract_function_parameters(node),
                    'return_type': self._extract_return_type(node),
                    'decorators': [self._get_name(decorator) for decorator in node.decorator_list],
                    'is_async': isinstance(node, ast.AsyncFunctionDef)
                }
                functions.append(function_info)
        
        return functions
    
    def _extract_path_from_decorator(self, decorator: ast.Call) -> str:
        """Extract path from FastAPI decorator"""
        if decorator.args:
            if isinstance(decorator.args[0], ast.Constant):
                return decorator.args[0].value
            elif isinstance(decorator.args[0], ast.Str):  # Python < 3.8
                return decorator.args[0].s
        return ""
    
    def _extract_function_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function parameters"""
        parameters = []
        
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'annotation': self._get_annotation(arg.annotation) if arg.annotation else None,
                'default': None
            }
            parameters.append(param)
        
        # Handle defaults
        if node.args.defaults:
            num_defaults = len(node.args.defaults)
            for i, default in enumerate(node.args.defaults):
                param_index = len(parameters) - num_defaults + i
                if param_index >= 0:
                    parameters[param_index]['default'] = self._get_default_value(default)
        
        return parameters
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation"""
        if node.returns:
            return self._get_annotation(node.returns)
        return None
    
    def _extract_endpoint_dependencies(self, node: ast.FunctionDef) -> List[str]:
        """Extract FastAPI dependencies"""
        dependencies = []
        
        for arg in node.args.args:
            if arg.annotation:
                annotation = self._get_annotation(arg.annotation)
                if 'Depends' in annotation:
                    dependencies.append(annotation)
        
        return dependencies
    
    def _extract_endpoint_middleware(self, node: ast.FunctionDef) -> List[str]:
        """Extract middleware applied to endpoint"""
        middleware = []
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and 'middleware' in decorator.id.lower():
                middleware.append(decorator.id)
        
        return middleware
    
    def _extract_model_fields(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract Pydantic model fields"""
        fields = []
        
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field = {
                    'name': item.target.id,
                    'type': self._get_annotation(item.annotation),
                    'default': self._get_default_value(item.value) if item.value else None
                }
                fields.append(field)
        
        return fields
    
    def _extract_model_validators(self, node: ast.ClassDef) -> List[str]:
        """Extract Pydantic validators"""
        validators = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Name) and 'validator' in decorator.id:
                        validators.append(item.name)
        
        return validators
    
    def _extract_db_operations(self, node: ast.FunctionDef) -> List[str]:
        """Extract database operations from function"""
        operations = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr in ['query', 'add', 'commit', 'delete', 'update', 'filter', 'join']:
                        operations.append(child.func.attr)
        
        return list(set(operations))
    
    def _extract_external_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract external API calls from function"""
        calls = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr in ['get', 'post', 'put', 'delete', 'request']:
                        calls.append(child.func.attr)
        
        return list(set(calls))
    
    def _extract_sqlalchemy_columns(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract SQLAlchemy columns"""
        columns = []
        
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if isinstance(item.value, ast.Call) and isinstance(item.value.func, ast.Name):
                            if item.value.func.id == 'Column':
                                column = {
                                    'name': target.id,
                                    'type': self._extract_column_type(item.value),
                                    'constraints': self._extract_column_constraints(item.value)
                                }
                                columns.append(column)
        
        return columns
    
    def _extract_sqlalchemy_relationships(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract SQLAlchemy relationships"""
        relationships = []
        
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if isinstance(item.value, ast.Call) and isinstance(item.value.func, ast.Name):
                            if item.value.func.id == 'relationship':
                                rel = {
                                    'name': target.id,
                                    'target': self._extract_relationship_target(item.value),
                                    'type': 'relationship'
                                }
                                relationships.append(rel)
        
        return relationships
    
    def _extract_table_name(self, node: ast.ClassDef) -> Optional[str]:
        """Extract SQLAlchemy table name"""
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == '__tablename__':
                        if isinstance(item.value, ast.Constant):
                            return item.value.value
                        elif isinstance(item.value, ast.Str):
                            return item.value.s
        return None
    
    def _extract_validation_logic(self, node: ast.FunctionDef) -> List[str]:
        """Extract validation logic patterns"""
        logic = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr in ['match', 'search', 'validate', 'check']:
                        logic.append(child.func.attr)
        
        return logic
    
    def _analyze_requirements(self, requirements_path: str) -> Dict[str, List[str]]:
        """Analyze requirements.txt"""
        dependencies = {'packages': []}
        
        try:
            with open(requirements_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        package = line.split('==')[0].split('>=')[0].split('<=')[0]
                        dependencies['packages'].append(package)
        except Exception as e:
            print(f"Error analyzing requirements.txt: {e}")
        
        return dependencies
    
    def _get_name(self, node) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return str(node)
    
    def _get_annotation(self, annotation) -> str:
        """Get type annotation as string"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return f"{self._get_name(annotation.value)}.{annotation.attr}"
        elif isinstance(annotation, ast.Subscript):
            return f"{self._get_name(annotation.value)}[{self._get_name(annotation.slice)}]"
        return str(annotation)
    
    def _get_default_value(self, node) -> Any:
        """Get default value from AST node"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.NameConstant):
            return node.value
        return None
    
    def _extract_column_type(self, call_node: ast.Call) -> str:
        """Extract SQLAlchemy column type"""
        if call_node.args:
            return self._get_name(call_node.args[0])
        return "Unknown"
    
    def _extract_column_constraints(self, call_node: ast.Call) -> List[str]:
        """Extract SQLAlchemy column constraints"""
        constraints = []
        
        for keyword in call_node.keywords:
            if keyword.arg in ['primary_key', 'nullable', 'unique', 'index']:
                constraints.append(f"{keyword.arg}={self._get_default_value(keyword.value)}")
        
        return constraints
    
    def _extract_relationship_target(self, call_node: ast.Call) -> str:
        """Extract SQLAlchemy relationship target"""
        if call_node.args:
            if isinstance(call_node.args[0], ast.Constant):
                return call_node.args[0].value
            elif isinstance(call_node.args[0], ast.Str):
                return call_node.args[0].s
        return "Unknown"