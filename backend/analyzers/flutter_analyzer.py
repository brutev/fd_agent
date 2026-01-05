import re
import os
import ast
from typing import Dict, List, Any, Optional, Tuple
import hashlib
from dataclasses import dataclass

@dataclass
class FlutterWidget:
    name: str
    type: str  # 'StatelessWidget', 'StatefulWidget', 'CustomWidget'
    file_path: str
    line_start: int
    line_end: int
    dependencies: List[str]
    api_calls: List[str]
    navigation_routes: List[str]
    form_fields: List[str]
    validators: List[str]

@dataclass
class BlocPattern:
    name: str
    type: str  # 'Bloc', 'Cubit'
    events: List[str]
    states: List[str]
    file_path: str

class FlutterAnalyzer:
    """Analyzes Flutter/Dart code to extract widgets, patterns, and dependencies"""
    
    def __init__(self):
        self.widgets = []
        self.blocs = []
        self.api_calls = []
        self.routes = []
        self.dependencies = {}
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze entire Flutter project"""
        results = {
            'widgets': [],
            'blocs': [],
            'api_calls': [],
            'routes': [],
            'dependencies': {},
            'theme_config': {},
            'navigation_structure': {}
        }
        
        # Analyze pubspec.yaml for dependencies
        pubspec_path = os.path.join(project_path, 'pubspec.yaml')
        if os.path.exists(pubspec_path):
            results['dependencies'] = self._analyze_pubspec(pubspec_path)
        
        # Analyze Dart files
        lib_path = os.path.join(project_path, 'lib')
        if os.path.exists(lib_path):
            for root, dirs, files in os.walk(lib_path):
                for file in files:
                    if file.endswith('.dart'):
                        file_path = os.path.join(root, file)
                        file_results = self.analyze_dart_file(file_path)
                        
                        results['widgets'].extend(file_results.get('widgets', []))
                        results['blocs'].extend(file_results.get('blocs', []))
                        results['api_calls'].extend(file_results.get('api_calls', []))
                        results['routes'].extend(file_results.get('routes', []))
        
        return results
    
    def analyze_dart_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single Dart file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'widgets': self._extract_widgets(content, file_path),
                'blocs': self._extract_bloc_patterns(content, file_path),
                'api_calls': self._extract_api_calls(content, file_path),
                'routes': self._extract_routes(content, file_path),
                'imports': self._extract_imports(content),
                'form_validators': self._extract_form_validators(content),
                'state_management': self._extract_state_management(content)
            }
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return {}
    
    def _extract_widgets(self, content: str, file_path: str) -> List[FlutterWidget]:
        """Extract Flutter widgets from Dart code"""
        widgets = []
        
        # Pattern for StatelessWidget
        stateless_pattern = r'class\s+(\w+)\s+extends\s+StatelessWidget\s*\{'
        for match in re.finditer(stateless_pattern, content):
            widget_name = match.group(1)
            start_line = content[:match.start()].count('\n') + 1
            
            # Find the end of the class
            end_line = self._find_class_end(content, match.start())
            
            widget = FlutterWidget(
                name=widget_name,
                type='StatelessWidget',
                file_path=file_path,
                line_start=start_line,
                line_end=end_line,
                dependencies=self._extract_widget_dependencies(content, match.start(), match.end()),
                api_calls=self._extract_widget_api_calls(content, match.start(), match.end()),
                navigation_routes=self._extract_widget_navigation(content, match.start(), match.end()),
                form_fields=self._extract_form_fields(content, match.start(), match.end()),
                validators=self._extract_widget_validators(content, match.start(), match.end())
            )
            widgets.append(widget)
        
        # Pattern for StatefulWidget
        stateful_pattern = r'class\s+(\w+)\s+extends\s+StatefulWidget\s*\{'
        for match in re.finditer(stateful_pattern, content):
            widget_name = match.group(1)
            start_line = content[:match.start()].count('\n') + 1
            end_line = self._find_class_end(content, match.start())
            
            widget = FlutterWidget(
                name=widget_name,
                type='StatefulWidget',
                file_path=file_path,
                line_start=start_line,
                line_end=end_line,
                dependencies=self._extract_widget_dependencies(content, match.start(), match.end()),
                api_calls=self._extract_widget_api_calls(content, match.start(), match.end()),
                navigation_routes=self._extract_widget_navigation(content, match.start(), match.end()),
                form_fields=self._extract_form_fields(content, match.start(), match.end()),
                validators=self._extract_widget_validators(content, match.start(), match.end())
            )
            widgets.append(widget)
        
        return widgets
    
    def _extract_bloc_patterns(self, content: str, file_path: str) -> List[BlocPattern]:
        """Extract BLoC/Cubit patterns"""
        blocs = []
        
        # BLoC pattern
        bloc_pattern = r'class\s+(\w+)\s+extends\s+Bloc<(\w+),\s*(\w+)>\s*\{'
        for match in re.finditer(bloc_pattern, content):
            bloc_name = match.group(1)
            event_type = match.group(2)
            state_type = match.group(3)
            
            events = self._extract_bloc_events(content, event_type)
            states = self._extract_bloc_states(content, state_type)
            
            bloc = BlocPattern(
                name=bloc_name,
                type='Bloc',
                events=events,
                states=states,
                file_path=file_path
            )
            blocs.append(bloc)
        
        # Cubit pattern
        cubit_pattern = r'class\s+(\w+)\s+extends\s+Cubit<(\w+)>\s*\{'
        for match in re.finditer(cubit_pattern, content):
            cubit_name = match.group(1)
            state_type = match.group(2)
            
            states = self._extract_bloc_states(content, state_type)
            
            cubit = BlocPattern(
                name=cubit_name,
                type='Cubit',
                events=[],
                states=states,
                file_path=file_path
            )
            blocs.append(cubit)
        
        return blocs
    
    def _extract_api_calls(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract API calls (dio, http)"""
        api_calls = []
        
        # Dio API calls
        dio_patterns = [
            r'dio\.get\([\'"]([^\'"]+)[\'"]',
            r'dio\.post\([\'"]([^\'"]+)[\'"]',
            r'dio\.put\([\'"]([^\'"]+)[\'"]',
            r'dio\.delete\([\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in dio_patterns:
            for match in re.finditer(pattern, content):
                api_calls.append({
                    'type': 'dio',
                    'method': pattern.split('\\')[1].split('(')[0],
                    'endpoint': match.group(1),
                    'file_path': file_path,
                    'line': content[:match.start()].count('\n') + 1
                })
        
        # HTTP package calls
        http_patterns = [
            r'http\.get\(Uri\.parse\([\'"]([^\'"]+)[\'"]',
            r'http\.post\(Uri\.parse\([\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in http_patterns:
            for match in re.finditer(pattern, content):
                api_calls.append({
                    'type': 'http',
                    'method': pattern.split('\\')[1].split('(')[0],
                    'endpoint': match.group(1),
                    'file_path': file_path,
                    'line': content[:match.start()].count('\n') + 1
                })
        
        return api_calls
    
    def _extract_routes(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract navigation routes"""
        routes = []
        
        # Navigator.pushNamed
        push_pattern = r'Navigator\.pushNamed\([^,]+,\s*[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(push_pattern, content):
            routes.append({
                'type': 'pushNamed',
                'route': match.group(1),
                'file_path': file_path,
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Route definitions
        route_pattern = r'[\'"]([^\'"/]+)[\'"]:\s*\([^)]+\)\s*=>\s*(\w+)\('
        for match in re.finditer(route_pattern, content):
            routes.append({
                'type': 'route_definition',
                'route': match.group(1),
                'widget': match.group(2),
                'file_path': file_path,
                'line': content[:match.start()].count('\n') + 1
            })
        
        return routes
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        import_pattern = r'import\s+[\'"]([^\'"]+)[\'"]'
        return [match.group(1) for match in re.finditer(import_pattern, content)]
    
    def _extract_form_validators(self, content: str) -> List[Dict[str, Any]]:
        """Extract form validators"""
        validators = []
        
        # TextFormField validators
        validator_pattern = r'validator:\s*\([^)]+\)\s*\{([^}]+)\}'
        for match in re.finditer(validator_pattern, content, re.DOTALL):
            validator_code = match.group(1)
            validators.append({
                'type': 'TextFormField',
                'code': validator_code.strip(),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return validators
    
    def _analyze_pubspec(self, pubspec_path: str) -> Dict[str, Any]:
        """Analyze pubspec.yaml for dependencies"""
        dependencies = {'dependencies': [], 'dev_dependencies': []}
        
        try:
            with open(pubspec_path, 'r') as f:
                content = f.read()
            
            # Extract dependencies
            dep_section = False
            dev_dep_section = False
            
            for line in content.split('\n'):
                line = line.strip()
                
                if line == 'dependencies:':
                    dep_section = True
                    dev_dep_section = False
                elif line == 'dev_dependencies:':
                    dep_section = False
                    dev_dep_section = True
                elif line.startswith('flutter:') or line.startswith('name:'):
                    dep_section = False
                    dev_dep_section = False
                elif dep_section and ':' in line and not line.startswith('#'):
                    dep_name = line.split(':')[0].strip()
                    dependencies['dependencies'].append(dep_name)
                elif dev_dep_section and ':' in line and not line.startswith('#'):
                    dep_name = line.split(':')[0].strip()
                    dependencies['dev_dependencies'].append(dep_name)
        
        except Exception as e:
            print(f"Error analyzing pubspec.yaml: {e}")
        
        return dependencies
    
    def _find_class_end(self, content: str, start_pos: int) -> int:
        """Find the end line of a class definition"""
        brace_count = 0
        in_class = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_class = True
            elif char == '}':
                brace_count -= 1
                if in_class and brace_count == 0:
                    return content[:i].count('\n') + 1
        
        return content.count('\n') + 1
    
    def _extract_widget_dependencies(self, content: str, start: int, end: int) -> List[str]:
        """Extract dependencies for a specific widget"""
        widget_content = content[start:end]
        dependencies = []
        
        # Look for common widget dependencies
        widget_patterns = [
            r'(\w+)\(',  # Widget constructors
            r'(\w+)\.of\(context\)',  # Provider/Theme access
        ]
        
        for pattern in widget_patterns:
            for match in re.finditer(pattern, widget_content):
                dep = match.group(1)
                if dep not in ['if', 'for', 'while', 'return'] and dep.istitle():
                    dependencies.append(dep)
        
        return list(set(dependencies))
    
    def _extract_widget_api_calls(self, content: str, start: int, end: int) -> List[str]:
        """Extract API calls within a widget"""
        widget_content = content[start:end]
        api_calls = []
        
        patterns = [
            r'dio\.(\w+)\(',
            r'http\.(\w+)\(',
            r'ApiClient\.(\w+)\('
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, widget_content):
                api_calls.append(match.group(1))
        
        return list(set(api_calls))
    
    def _extract_widget_navigation(self, content: str, start: int, end: int) -> List[str]:
        """Extract navigation calls within a widget"""
        widget_content = content[start:end]
        navigation = []
        
        nav_patterns = [
            r'Navigator\.push\w*\([^,]+,\s*[\'"]([^\'"]+)[\'"]',
            r'context\.go\([\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in nav_patterns:
            for match in re.finditer(pattern, widget_content):
                navigation.append(match.group(1))
        
        return navigation
    
    def _extract_form_fields(self, content: str, start: int, end: int) -> List[str]:
        """Extract form fields within a widget"""
        widget_content = content[start:end]
        fields = []
        
        field_patterns = [
            r'TextFormField\(',
            r'DropdownButtonFormField\(',
            r'CheckboxFormField\(',
            r'RadioFormField\('
        ]
        
        for pattern in field_patterns:
            fields.extend([pattern.split('(')[0] for _ in re.finditer(pattern, widget_content)])
        
        return fields
    
    def _extract_widget_validators(self, content: str, start: int, end: int) -> List[str]:
        """Extract validators within a widget"""
        widget_content = content[start:end]
        validators = []
        
        validator_patterns = [
            r'Validators\.(\w+)',
            r'validator:\s*(\w+)'
        ]
        
        for pattern in validator_patterns:
            for match in re.finditer(pattern, widget_content):
                validators.append(match.group(1))
        
        return list(set(validators))
    
    def _extract_bloc_events(self, content: str, event_type: str) -> List[str]:
        """Extract BLoC events"""
        events = []
        event_pattern = f'class\\s+(\\w+)\\s+extends\\s+{event_type}'
        
        for match in re.finditer(event_pattern, content):
            events.append(match.group(1))
        
        return events
    
    def _extract_bloc_states(self, content: str, state_type: str) -> List[str]:
        """Extract BLoC states"""
        states = []
        state_pattern = f'class\\s+(\\w+)\\s+extends\\s+{state_type}'
        
        for match in re.finditer(state_pattern, content):
            states.append(match.group(1))
        
        return states
    
    def _extract_state_management(self, content: str) -> Dict[str, List[str]]:
        """Extract state management patterns"""
        patterns = {
            'provider': [],
            'riverpod': [],
            'bloc': [],
            'getx': []
        }
        
        # Provider patterns
        provider_patterns = [
            r'Provider<(\w+)>',
            r'ChangeNotifierProvider<(\w+)>',
            r'Consumer<(\w+)>'
        ]
        
        for pattern in provider_patterns:
            for match in re.finditer(pattern, content):
                patterns['provider'].append(match.group(1))
        
        # BLoC patterns
        bloc_patterns = [
            r'BlocProvider<(\w+)>',
            r'BlocBuilder<(\w+),\s*(\w+)>',
            r'BlocListener<(\w+),\s*(\w+)>'
        ]
        
        for pattern in bloc_patterns:
            for match in re.finditer(pattern, content):
                patterns['bloc'].append(match.group(1))
        
        return patterns